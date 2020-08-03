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

jdx_version = '1.0.1'

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


# == Functions definitions

def block_heading(lines):
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
    meta['ndeps'] += 1
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
    meta.update({'npkgs': 0, 'nsrcs': 0, 'ndeps': 0, 'ncycs': 0})
    with open(infile) as f:
        for line in f:
            fn = parser_dispatch[line[0]]
            item, item_list = fn(line[1:].strip())
            item_list.append(item)


def augment_meta():
    meta['title'], meta['date'], meta['file'] = comments[:3]
    meta['basename'] = meta['file'].replace('.data', '')


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
    dump_list('cycles', cycles)
    dump_list('roots', roots)

    dump_dict('meta', meta)


# === TEMPLATES to be inserted into the HTML page ===========================
'''
c_red = '#ff0000'
c_yellow = '#d59800'
c_green = '#2ca02c'
c_blue = 'steelblue'
c_grey = '#bbb'
'''

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

#sidebar {
    position: relative;
}

#ver {
    position: absolute;
    bottom: 12px;
    left: 12px;
    color: #d4c2a0;
    font-size: 12px;
    font-style: italic;
    padding: 4px;
}

#sidebar .panel {
    margin: 10px 10px 20px 10px;
    background-color: #ffffff;
    box-shadow: 2px 2px 4px 2px #777777;
    padding: 5px;
    width: 220px;
}

#sidebar .panel.hideable {
    display: none;
}

#sidebar .panel.hideable.root {
    color: #66d;
}
#sidebar .panel.hideable.incyc {
    color: #f00;
}

#detail-pane {
    opacity: 0.5;
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
}

#lists {
    display: flex;
    justify-content: flex-start;
}
#lists>div {
    min-width: 200px;
    margin: 8px;
    padding: 8px;
    border: 1px dotted steelblue;
    background-color: white;
}
#lists>div h2 {
    border-bottom: 2px dotted #ddd;
    margin-bottom: 6px;
    color: #c0d4d4;
}

.item {
    padding: 2px;
}
.item:hover {
    background-color: #888;
    color: white;
}
.item.selected {
    background-color: #888;
    color: white;
    font-weight: bold;
}

.item.root {
    color: #88f;
}
.item.root:hover {
    background-color: #66d;
    color: white;
}
.item.root.selected {
    background-color: #bbe;
    color: white;
}

.item.incyc {
    color: #f00;
}
.item.incyc:hover {
    background-color: #d00;
    color: white;
}
.item.incyc.selected {
    background-color: #fcc;
    color: white;
}

"""

struct_template = """
<div id="container">
  <div id="sidebar">
    <div id="summary-pane" class="panel clickable">
        <h1></h1>
        <div class="stat-list"></div>
    </div>
    <div id="select-pane" class="panel hideable">
        <h1></h1>
        <div class="stat-list"></div>
    </div>
    <div id="detail-pane" class="panel hideable">
        <h1></h1>
        <div class="stat-list"></div>
    </div>
    <div id="ver"></div>
  </div>

<div id="lists">
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
                         'src="https://code.jquery.com/jquery-3.5.1.min.js"\n        ' + \
                         'integrity="sha256-9/aliU8dGd2tb6OSsuzixeV4y/faTqgFtohetphbbj0="\n        ' + \
                         'crossorigin="anonymous"></script>\n'

script_template = """
/* -------------- */
/* Internal State */
/* -------------- */

const $sump = $('#summary-pane');
const $selp = $('#select-pane');
const $detp = $('#detail-pane');
const $lists = $('#lists');
const $plist = $('#pkg-list .content');
const $slist = $('#src-list .content');
const $ilist = $('#imp-list .content');

const sel = {
    pi: -1,
    si: -1,
    $p: null,
    $s: null,
};

const srcDepMap = {};
const cycles = [];
const pkgCycMap = {};


/* -------------------- */
/* Function Definitions */
/* -------------------- */

const logVersion = () => {
    $('#ver').text("JDX " + jdxVersion);
    console.log('JDX version', jdxVersion);
    console.log('jQuery version', $().jquery);
};

const inflateData = () => {
    console.log('Inflating data...')
    
    codedDeps.forEach(d => {
        let [src, tgt] = d.split('>');
        let impList = srcDepMap[src];
        if (!impList) {
            impList = [];
            srcDepMap[src] = impList;
        }
        impList.push(tgt);
    });
    
    codedCycles.forEach((c, ci) => {
      let cp = c.split("}");
      cp.pop();
      cycles.push(cp);
      cp.forEach(pi => {
        let cis = pkgCycMap[pi] || [];
        cis.push(ci);
        pkgCycMap[pi] = cis;
      });
    });
    //console.log('cycles...', cycles);
    //console.log('package cycles...', pkgCycMap);
};

const div = cls => $('<div>').addClass(cls);
const clickable = $d => $d.addClass('clickable');


/* --- SIDEBAR panels --- */

const addStat = ($div, lab, val) => {
    const $l = div('stat-label').html(lab);
    const $v = div('stat-value').html(val);
    const $si = div('stat-item').append($l).append($v);
    $div.append($si);
}

const nextItem = (arr, item) => {
  let n = arr.indexOf(item) + 1;
  n = n === arr.length ? 0 : n;
  return arr[n];
};

const getDeps = (pi, pCyc) => {
  let tagNext = {};
  pCyc.forEach(ci => {
    tagNext[nextItem(cycles[ci], pi)] = 1;
  });
  return Object.keys(tagNext);
};

const popCycLinks = ($sl, pi, pCyc) => {
  getDeps(pi, pCyc).forEach(k => {
    addStat($sl, '&rarr;', insSpaces(xP(k)));
  });
};
    
const popSummary = () => {
    $sump.find('h1').text(`Project ${jdxMeta.basename}`);
    const $sl = $sump.find('.stat-list');
    addStat($sl, "Packages", jdxMeta.npkgs);
    addStat($sl, "Classes", jdxMeta.nsrcs);
    addStat($sl, "Cycles", jdxMeta.ncycs);
    addStat($sl, "Roots", jdxMeta.nroots);
};

$sump.click(ev => deselectPackage());

const updateStatsPane = ($pane, pi) => {
    let nSrc = sources[pi].length;
    
    let isRoot = codedRoots.includes(parseInt(pi, 10));
    $pane.toggleClass('root', isRoot);
    
    let pCyc = pkgCycMap[pi] || [];
    let nCyc = pCyc.length;
    let inCyc = nCyc > 0;
    $pane.toggleClass('incyc', inCyc);
    
    $pane.find('h1').text(insSpaces(xP(pi)));
    const $sl = $pane.find('.stat-list');
    $sl.empty();
    isRoot && addStat($sl, "Root", "(no dependencies)");
    addStat($sl, "Classes", nSrc);
    inCyc && addStat($sl, "In Cycles", nCyc); 
    inCyc && popCycLinks($sl, pi, pCyc);
};

const fillPkgDetails = pi => {
    updateStatsPane($detp, pi);
};

const updateSelPane = () => {
    updateStatsPane($selp, sel.pi);
};


/* --- DATA wrangling --- */

const insSpaces = z => z.replace(/\\./g, ' .');

const xP = x => packages[x];
const xPStr = x => `${xP(x)} (${sources[x].length})`;
const xxPSi = xx => xx.split('.');
const xxS = xx => {
    let [p, s] = xxPSi(xx);
    return sources[p][s];
};
const xxSStr = xx => {
    let deps = srcDepMap[xx] || []
    return `${xxS(xx)} (${deps.length})`
};
const xxFqSStr = xx => {
    let [p, s] = xxPSi(xx);
    return `${xP(p)}.${sources[p][s]}`
};

const pkgsFromFqsiList = arr => {
    let pTags = {};
    arr.forEach(fq => {
      pTags[fq.split('.')[0]] = 1;
    });
    return Object.keys(pTags);
};
 
const pkgsInCycs = arr => {
    let inCycs = Object.keys(pkgCycMap);
    return arr.filter(pi => inCycs.includes(pi));
};

const navTo = ssi => {
    console.log('** NAV TO **', ssi);
    deselectPackage();
    const [p, s] = xxPSi(ssi);
    doPClick($plist.find(`.item[data-idx="${p}"]`));
    doSClick($slist.find(`.item[data-idx="${s}"]`));
};


/* --- PACKAGE list --- */

const packageHover = pi => {
    fillPkgDetails(pi);
    $detp.show();
};

const clearHover = () => {
    $detp.hide();
};

const pkgRef = pi => `[${pi}] ${xP(pi)}`;

$plist.click(ev => doPClick($(ev.target)));

const doPClick = $p => {
    if (sel.$p) {
        deselectPackage();
    }
    selectPackage($p, $p.attr('data-idx'));
};

const deselectPackage = () => {
    sel.$p && sel.$p.removeClass('selected');
    sel.$p = null;
    sel.pi = -1;
    clearSourceList();
    clearImportList();
    $selp.hide();
};

const selectPackage = ($p, pi) => {
    console.log(`Selecting package ${pkgRef(pi)}`);
    
    $p.addClass('selected');
    sel.$p = $p;
    sel.pi = pi;
    popSourceList(pi);
    updateSelPane();
    $selp.show();
};

const popPackageList = () => {
    for (let pi=0; pi<packages.length; pi++) {
        let $item = clickable(div('item').text(xPStr(pi)));
        $item.attr('data-idx', pi);
        $item.hover(ev => packageHover($(ev.target).attr('data-idx')),
                    ev => clearHover());
        // mark root packages
        codedRoots.includes(pi) && $item.addClass('root').attr('data-root', 1);
        // mark packages that are found in cycles
        pkgCycMap[pi] && $item.addClass('incyc');
                
        $plist.append($item);
    }
};


/* --- SOURCE list --- */

const mkFqsi = si => sel.pi < 0 ? `-.${si}` : `${sel.pi}.${si}`;

const srcRef = si => {
    let fqsi = mkFqsi(si);
    return `[${fqsi}] ${xxFqSStr(fqsi)}`;
};

$slist.click(ev => doSClick($(ev.target)));

const doSClick = $s => {
    let si = $s.attr('data-idx');
    sel.$s && deselectSource();
    selectSource($s, si);
};

const deselectSource = () => {
    sel.$s.removeClass('selected');
    clearImportList();
};

const selectSource = ($s, si) => {
    console.log(`Selecting source ${srcRef(si)}`);
    
    $s.addClass('selected');
    sel.$s = $s;
    sel.si = si;
    popImportList(si);
};

const popSourceList = pi => {
    for (let si=0; si<sources[pi].length; si++) {
        let fq = mkFqsi(si);
        let sdeps = srcDepMap[fq] || [];
        let depps = pkgsFromFqsiList(sdeps);
        let cycps = pkgsInCycs(depps);
        let inCyc = cycps.length > 0;
        
        let $item = clickable(div('item').text(xxSStr(mkFqsi(si))));
        $item.attr('data-idx', si);
        $item.attr('data-depp', depps);
        $item.attr('data-depc', cycps);
        $item.toggleClass('incyc', inCyc);
        
        $slist.append($item);
    }
};

const clearSourceList = () => {
    $slist.empty();
    sel.$s = null;
    sel.si = -1;
};


/* --- IMPORT list --- */

$ilist.click(ev => {
    let $tgt = $(ev.target);
    let ssi = $tgt.attr('data-dd');
    console.log(`Clicked on import [${ssi}] ${xxFqSStr(ssi)}`);
    navTo(ssi);
});

const popImportList = si => {
    let deps = srcDepMap[mkFqsi(si)] || [];
    let ddps = pkgsFromFqsiList(deps);
    let cycps = pkgsInCycs(ddps);

    deps.forEach(dd => {
        let [p, s] = dd.split('.');
        let inCyc = cycps.includes(p);
        
        let $item = clickable(div('item').text(xxFqSStr(dd)));
        $item.attr('data-dd', dd);
        $item.toggleClass('incyc', inCyc);
        
        $ilist.append($item);
    });
};

const clearImportList = () => {
    $ilist.empty();
};

"""

version_template = f'const jdxVersion = "{jdx_version}";\n\n'

mainline_template = """
/* ------------------------- */
/* Mainline Code starts here */
/* ------------------------- */

console.log('Now under New Management!');

logVersion();
inflateData();
popSummary();
popPackageList();
"""

# -------------------------------------------------------------------------
# == Python "constants"

html_template_start = '<!DOCTYPE html>\n<html>\n<head>\n'
html_template_meta = '    <meta charset="utf-8">\n'
html_template_middle = '</head>\n<body>\n'
html_template_end = '</body>\n</html>\n'


# -------------------------------------------------------------------------
# == More function definitions

def wr_title(hf):
    hf.write(f'    <title>{meta["basename"]} JDX</title>\n')


def wr_style(hf):
    hf.write('    <style>\n')
    hf.write(css_template)
    hf.write('    </style>\n')


def wr_struct(hf):
    hf.write(struct_template)


def wr_jdx_data(hf):
    hf.write('/* ------------ */\n')
    hf.write('/* Project Data */\n')
    hf.write('/* ------------ */\n\n')
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
    hf.write(version_template)
    hf.write(mainline_template)
    hf.write('</script>\n')


def populate_html_head(hf):
    wr_title(hf)
    wr_style(hf)


def populate_html_body(hf):
    wr_struct(hf)
    wr_script(hf)


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
    block_heading(['Java Source', 'Package Dependency Explorer', 'Generator'])

    datafile = basename + data_suffix
    htmlfile = basename + html_suffix
    if not os.path.isfile(datafile):
        print(f'No data file found: "{datafile}"')
        exit(1)

    print(f'Reading from file: {datafile}...')
    parse_data_file(datafile)
    augment_meta()
    find_roots()
    report()

    print(f'\nWriting to file: {htmlfile}...')
    write_html(htmlfile)

    print('\nDone')


main()
