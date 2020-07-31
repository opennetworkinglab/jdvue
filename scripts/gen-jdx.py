"""
gen-jdx.py

    Generates a standalone web page that facilitates exploration of
    Java Dependencies of a code base. Requires a JDVue detail-data
    file as input.

Usage:
    python gen-jdx.py <datafile-basename>

  where:
    <datafile-basename> is the basename of the detail data file. For
        example, "./myproject", if the data file is "./myproject.data".

Output:
    <datafile-basename>.jdx.html        -- JDX visualization

Author: Simon Hunt / July 2020
"""

import os
import sys

# == Script Constants

jdx_version = '1.0'

# some colors
c_red = '#ff0000'
c_yellow = '#d59800'
c_green = '#2ca02c'
c_blue = 'steelblue'
c_grey = '#bbb'

# == Other configuration values

data_suffix = '.data'
html_suffix = '.jdx.html'

# == Globals
meta = {}
comments = []
packages = []
package_map = {}
dependencies = []
cycles = []
non_roots = set()
roots = []

current_package = None

decode_pkg = {}
decode_src_map = {}
src_dep_map = {}
expanded_cycles = []


def print_block_heading(lines):
    def center(txt, size):
        spc = size - len(txt)
        left = spc // 2
        right = spc - left
        return f'{" " * left}{txt}{" " * right}'

    maxlen = max([len(x) for x in lines])
    lineseg = '-' * maxlen
    print()
    print(f'+---{lineseg}---+')
    for line in lines:
        print(f'|   {center(line, maxlen)}   |')
    print(f'+---{lineseg}---+')
    print()


def set_if_absent(dic, key, setval):
    if key not in dic:
        dic[key] = setval
    return dic[key]


def parse_comment(com):
    return com, comments


def parse_package(pkg):
    global current_package
    current_package = pkg
    meta['npkgs'] += 1
    return pkg, packages


def parse_source(src):
    srclist = set_if_absent(package_map, current_package, [])
    meta['nsrcs'] += 1
    return src, srclist


def parse_dependency(dep):
    non_root_pkg_code = int(dep.split('.')[0])
    non_roots.add(non_root_pkg_code)
    return dep, dependencies


def parse_cycle(cyc):
    meta['ncycs'] += 1
    return cyc, cycles


parser_dispatch = {
    ';': parse_comment,
    'P': parse_package,
    'S': parse_source,
    'D': parse_dependency,
    'C': parse_cycle,
}


def usage_then_exit():
    print(f'Usage: python {sys.argv[0]} <datafile-basename>')
    exit(1)


def reslash(s):
    return s.replace('\\', '/')


def clean_dir_name(d):
    d = reslash(d)
    if d.endswith('/'):
        d = d[:-1]
    return d


def get_cmdline_args():
    if len(sys.argv) != 2:
        usage_then_exit()
    basename = clean_dir_name(sys.argv[1])
    basename = basename[:-len(data_suffix)] \
        if basename.endswith(data_suffix) \
        else basename
    return basename


def parse_data_file(infile):
    meta.update({'npkgs': 0, 'nsrcs': 0, 'ncycs': 0})
    with open(infile) as f:
        for line in f:
            fn = parser_dispatch[line[0]]
            item, item_list = fn(line[1:].strip())
            item_list.append(item)


def populate_meta():
    meta['title'], meta['date'], meta['file'] = comments[:3]
    meta['basename'] = meta['file'].replace('.data', '')


"""
def create_decode_maps():
    for pidx in range(len(packages)):
        decode_pkg[str(pidx)] = packages[pidx]

    for pkg, src_list in package_map.items():
        src_map = set_if_absent(decode_src_map, pkg, {})
        for sidx in range(len(src_list)):
            src_map[str(sidx)] = src_list[sidx]


def decode_dotted_source(dotted):
    # returns package and fully qualified source
    pidx, sidx = dotted.split('.')
    pkg = decode_pkg[pidx]
    src = decode_src_map[pkg][sidx]
    return pkg, f'{pkg}.{src}'


def decode_dependencies():
    for enc_dep in dependencies:
        src_code, tgt_code = enc_dep.split('>')
        src_p, src_s = decode_dotted_source(src_code)
        tgt_p, tgt_s = decode_dotted_source(tgt_code)
        dep_map = set_if_absent(src_dep_map, src_s, [])
        dep_map.append(tgt_s)
        non_roots.add(src_p)


def decode_cycle(cyc):
    return [decode_pkg[p] for p in cyc.split('}') if p]


def decode_cycles():
    for cyc in cycles:
        expanded_cycles.append(decode_cycle(cyc))


def compute_dep_roots():
    global roots
    allpkgs = set(packages)
    rootset = allpkgs.difference(non_roots)
    roots = sorted(list(rootset))
    meta['nroots'] = len(roots)

"""


def find_roots():
    global roots
    all_pkg_codes = set(range(len(packages)))
    root_set = sorted(list(all_pkg_codes.difference(non_roots)))
    roots = [str(r) for r in root_set]
    meta['nroots'] = len(roots)


def dump_list(tag, lst):
    print(f'\n{tag} ...')
    for x in lst:
        print(f'  {x}')


def dump_dict(tag, dic):
    print(f'\n{tag} ...')
    for k, v in dic.items():
        print(f'  {k} -> {v}')


def report():
    # dump_list('comments', comments)
    dump_list('packages', packages)
    dump_dict('package map', package_map)
    dump_list('dependencies', dependencies)
    dump_list('cycles', cycles)
    dump_list('roots', roots)
    """
    dump_list('non-roots', non_roots)

    dump_dict('decode package', decode_pkg)
    dump_dict('decode sources', decode_src_map)
    dump_dict('source dep map', src_dep_map)
    dump_list('decoded cycles', expanded_cycles)
    """

    dump_dict('meta', meta)


# === TEMPLATES to be inserted into the HTML page ===========================

css_color_template = f"""
.red {{ color: {c_red}; }}
.yellow {{ color: {c_yellow}; }}
.green {{ color: {c_green}; }}
.blue {{ color: {c_blue}; }}
.grey {{ color: {c_grey}; }}
"""

css_template = """
body {
    font: 300 13px "Helvetica Neue", Helvetica, Arial, sans-serif;
    color: #044;
}

h1 {
    font-size: 16px;
    font-weight: bold;
    margin: 0;
    padding: 0;
}

h2 {
    font-size: 14px;
    font-weight: bold;
    margin: 0;
    padding: 0;
}

#ver {
    position: fixed;
    top: 16px;
    right: 16px;
    color: #999;
    font-size: 12px;
    font-style: italic;
    padding: 4px;
}

#container {
    min-height: 600px;
    display: flex;
    padding: 4px;
}
#container>div {
    background-color: #efe8db;
    margin: 0px;
    padding: 4px;
    border: 1px solid white;
}

#sidebar>div {
    margin: 10px 10px 20px 10px;
    background-color: #ffffff;
    box-shadow: 2px 2px 4px 2px #777777;
    padding: 5px;
    width: 192px;
}

#detail-pane {
    display: none;
    color: #6ad;
}

.clickable {
    cursor: pointer;
}

.stat-item {
    margin: 2px 6px;
    display: flex;
    justify-content: space-between;
}
.stat-label {
}
.stat-value {
    font-weight: bold;
}

#top {
    display: flex;
    justify-content: flex-start;
}
#top>div {
    margin: 8px;
    padding: 8px;
    border: 1px dotted steelblue;
    background-color: white;
}
#top>div h2 {
    border-bottom: 2px dotted #ddd;
    margin-bottom: 6px;
    color: #c0d4d4;
}

.pkg-item {
    padding: 2px;
}
.pkg-item:hover {
    background-color: #6ad;
    color: white;
}
.pkg-item.selected {
    background-color: #c5e1ff;
    color: black;
    font-weight: bold;
}

.src-item {
    padding: 2px;
}
.src-item:hover {
    background-color: #6ad;
    color: white;
}
.src-item.selected {
    background-color: #c5e1ff;
    color: black;
    font-weight: bold;
}

"""

struct_template = """
<div id="ver"></div>
<div id="container">
  <div id="sidebar">
    <div id="summary-pane">
        <h1></h1>
        <div class="stat-list"></div>
    </div>
    <div id="detail-pane">
        <h1></h1>
        <div class="stat-list"></div>
    </div>
  </div>

<div id="top">
    <div id="pkg-list">
        <h2>Packages</h2>
        <div class="content"></div>
    </div>
    <div id="src-list">
        <h2>Classes</h2>
        <div class="content"></div>
    </div>
    <div id="imp-list">
        <h2>Imports</h2>
        <div class="content"></div>
    </div>
</div>
</div>
"""

jquery_351min_template = '<script ' + \
                         'src="https://code.jquery.com/jquery-3.5.1.min.js" ' + \
                         'integrity="sha256-9/aliU8dGd2tb6OSsuzixeV4y/faTqgFtohetphbbj0=" ' + \
                         'crossorigin="anonymous"></script>\n'

version_template = f'const jdxVersion = "{jdx_version}";\n'

script_template = version_template + """
$('#ver').text("JDX " + jdxVersion);

const logVersion = () => {
    console.log('JDX version', jdxVersion);
    console.log('jQuery version', $().jquery);
};

const $top = $('#top');
const $sump = $('#summary-pane');
const $detp = $('#detail-pane');

const sel = {
    pi: -1,
    si: -1,
    fqsi: '',
    $p: null,
    $s: null,
};

const div = cls => $('<div>').addClass(cls);

const addStat = ($div, lab, val) => {
    const $l = div('stat-label').text(lab + ':');
    const $v = div('stat-value').text(val);
    const $si = div('stat-item').append($l).append($v);
    $div.append($si);
}

const popSummary = () => {
    $sump.find('h1').text(`Project ${jdxMeta.basename}`);
    const $sl = $sump.find('.stat-list');
    addStat($sl, "Sources", jdxMeta.nsrcs);
    addStat($sl, "Packages", jdxMeta.npkgs);
    addStat($sl, "Cycles", jdxMeta.ncycs);
    addStat($sl, "Roots", jdxMeta.nroots);
};

// packages []
// sources [ [], [], ... ]
// codedDeps []
// codedCycles []
// codedRoots []

//const srcDepMap = {};
//const expandedCycles = [];

const xP = x => packages[x];
const xPStr = x => `${xP(x)} (${sources[x].length})`;

const xxPSi = xx => xx.split('.');
const xxS = xx => {
    let [p, s] = xxPSi(xx);
    return sources[p][s];
};
const xxSStr = xx => {
    let [p, s] = xxPSi(xx);
    let pname = xP(p);
    let sname = sources[p][s];
    let ni = 0;
    return `${pname}.${sname} (${ni})`
};





const xFQS = x => {
    let z = x.split(".");
    let p = xP(z[0]);
    let s = sources[z[0]][z[1]];
    return `${p}.${s}`;
};

const clickable = $d => $d.addClass('clickable');

const fillPkgDetails = pi => {
    $detp.find('h1').text(xP(pi));
    const $sl = $detp.find('.stat-list');
    $sl.empty();
    addStat($sl, "Sources", sources[pi].length);
};

const packageHover = pi => {
    fillPkgDetails(pi);
    $detp.show();
};

const clearHover = () => {
    $detp.hide();
};

const pkgRef = pi => `[${pi}] ${xP(pi)}`;

$('#pkg-list .content').click(ev => {
    let $p = $(ev.target);
    let pi = $p.data('idx');
    console.log(`Clicked on package ${pkgRef(pi)}`);
    if (sel.$p) {
        deselectPackage();
    }
    selectPackage($p, pi);
});

const deselectPackage = () => {
    console.log(`Deselecting package ${pkgRef(sel.pi)}`);
    sel.$p.removeClass('selected');
    sel.$p = null;
    sel.pi = -1;
    clearSourceList();
};

const selectPackage = ($p, pi) => {
    console.log(`Selecting package ${pkgRef(pi)}`);
    $p.addClass('selected');
    sel.$p = $p;
    sel.pi = pi;
    popSourceList(pi);
};

const popPackageList = () => {
    const $pl = $('#pkg-list .content');

    for (let pi=0; pi<packages.length; pi++) {
        let $item = clickable(div('pkg-item').text(xPStr(pi)));
        $item.data('idx', pi);

        // TODO: add classes for roots/cyclics

        $item.hover(ev => packageHover($(ev.target).data('idx')),
                    ev => clearHover());

        $pl.append($item);
    }
};

const mkFqsi = si => sel.pi < 0 ? `-.${si}` : `${sel.pi}.${si}`;

const srcRef = si => {
    let fqsi = mkFqsi(si);
    return (sel.pi < 0) ? `[${fqsi}] ???` : `[${fqsi}] ${xFQS(fqsi)}`;
};

$('#src-list .content').click(ev => {
    let $s = $(ev.target);
    let si = $s.data('idx');
    console.log(`Clicked on source ${srcRef(si)}`);
    if (sel.$s) {
        deselectSource();
    }
    selectSource($s, si);
});

const deselectSource = () => {
    console.log(`Deselecting Source ${srcRef(sel.si)}`);
    sel.$s.removeClass('selected');
    sel.$s = null;
    sel.si = -1;
    //clearImportList();
};

const selectSource = ($s, si) => {
    console.log(`Selecting source ${srcRef(si)}`);
    $s.addClass('selected');
    sel.$s = $s;
    sel.si = si;
    //popImportList(si);
};


const popSourceList = pi => {
    const $sl = $('#src-list .content');

    for (let si=0; si<sources[pi].length; si++) {
        let fqsi = mkFqsi(si);
        let $item = clickable(div('src-item').text(xxSStr(fqsi)));
        $item.data('idx', si);

        // TODO: add classes for this source

//        $item.hover(ev => packageHover($(ev.target).data('idx')),
//                    ev => clearHover());

        $sl.append($item);
    }
};

const clearSourceList = () => {
    $('#src-list .content').empty();
};



/* Mainline Code starts here */

logVersion();
popSummary();
popPackageList();

"""


def wr_title(hf):
    hf.write(f'    <title>{meta["basename"]} JDX</title>\n')


def wr_style(hf):
    hf.write('    <style>\n')
    hf.write(css_template)
    hf.write(css_color_template)
    hf.write('    </style>\n')


def wr_struct(hf):
    hf.write(struct_template)


def wr_jdx_data(hf):
    hf.write('const jdxMeta = {\n')
    for k, v in meta.items():
        vstr = f'"{v}"' if type(v) == str else f'{v}'
        hf.write(f'  "{k}": {vstr},\n')
    hf.write('};\n')

    p_code = {}
    pi = 0
    hf.write('const packages = [\n')
    for p in packages:
        p_code[p] = pi
        pi += 1
        hf.write(f'  "{p}",\n')
    hf.write('];\n')

    hf.write('const sources = [\n')
    for p, ss in package_map.items():
        hf.write(f'  [')
        for s in ss:
            hf.write(f' "{s}",')
        hf.write(' ],\n')
    hf.write('];\n')

    hf.write('const codedDeps = [\n')
    for d in dependencies:
        hf.write(f'  "{d}",\n')
    hf.write('];\n')

    hf.write('const codedCycles = [\n')
    for c in cycles:
        hf.write(f'  "{c}",\n')
    hf.write('];\n')

    hf.write('const codedRoots = [')
    for r in roots:
        hf.write(f'{r},')
    hf.write('];\n')


def wr_script(hf):
    hf.write(jquery_351min_template)
    hf.write('<script>\n')
    wr_jdx_data(hf)
    hf.write(script_template)
    hf.write('</script>\n')


def populate_html_head(hf):
    wr_title(hf)
    wr_style(hf)


def populate_html_body(hf):
    wr_struct(hf)
    wr_script(hf)


html_template_start = '<!DOCTYPE html>\n<html>\n<head>\n'
html_template_meta = '    <meta charset="utf-8">\n'
html_template_middle = '</head>\n<body>\n'
html_template_end = '</body>\n</html>\n'


def write_html(htmlfile):
    with open(htmlfile, 'w') as hf:
        hf.write(html_template_start)
        hf.write(html_template_meta)
        populate_html_head(hf)
        hf.write(html_template_middle)
        populate_html_body(hf)
        hf.write(html_template_end)


def main():
    basename = get_cmdline_args()
    print_block_heading([
        'Java Source', 'Package Dependency Explorer', 'Generator'
    ])

    datafile = basename + data_suffix
    htmlfile = basename + html_suffix
    if not os.path.isfile(datafile):
        print(f'No data file found: "{datafile}"')
        exit(1)

    print(f'Reading from file: {datafile}...')
    parse_data_file(datafile)
    populate_meta()
    find_roots()

    # TODO: --- these will be written in JavaScript
    # create_decode_maps()
    # decode_dependencies()
    # decode_cycles()

    report()

    print(f'\nWriting to file: {htmlfile}...')
    write_html(htmlfile)

    print('\nDone')


main()
