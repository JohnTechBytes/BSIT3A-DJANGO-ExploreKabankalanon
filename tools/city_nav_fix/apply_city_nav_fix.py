#!/usr/bin/env python3
"""Remove the duplicate in-page site navigation; preserve the shared header."""
import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import tempfile
from datetime import datetime
import zlib

FILES = {'templates/info/city_information.html': (('bcde7c8decbaaad9dabfe7bf0ca98ab882ae6fe25a60f714472673cf6ad7fe5c',),
                                          '4b280087cd9b9da62b5bcbf169bae6d7f58d94ab36027be8bc78e30845522b25')}

PREREQUISITES = {}

PAYLOAD = json.loads(zlib.decompress(base64.b85decode(
    'c-pO4*>d7a68)Ecb;MjPR<|_~_rZV>!dMLgwA9Ol7LWubLA2P!jrsRESrQo8bobnec_3^pRh7%hlPC4pm)#=Y@?f_p|Hz8v=8q`b'
    'RsW*@e&oR}+Z6vucRBy^&o7H=o-i+!n5(U$>N$&zl!xy85DlCxH2BI>hH0eC_rbv4g<UfldeSSc2@O4E-Of2S`cmM&UGMw(>EJ76'
    '5*u6!jXCbiy}+|I^M&tOu2-Q;@9TT>?Nv2joX5yG9irSB`R*_c^IaMm{k^aW_FVS*xVN9{>xHAQ@a`El^QC8PV`IK!M!yQG&Wg?('
    'xpdysE;9NBn|63m$?L$gR-wvxRIGQ6pE#%71-ULqxyBb$Sqcni$Gno8hO=kJunZOJhuL-XZbA2&>w)zn@H$JxXCKh{vr}psR_S}z'
    'c|0ASSyw&>3O|}zX9M5z@zh+w?`@dLt5DG>){?o>X5yWJeZbm7SlB!)CQl>f<>9yf7ZfXd=_~p^hMjSjVnFusy|0{PhPa!By<x7*'
    'N3xzpd4JEk+9o#S(#$UJ{=z?l9YWRS5x=a(n)&~hE9CqD8!Jz>Q>L7@VJ<My+QWQ7{s!yPe9<^lhli-@jD5x0GV;ynm%lv&_=TNI'
    'U$xGj($DEU@@Z_)d1V5dOUg?;;3e}c#Kn=`b2I!loZjGAv4AQ43=Hv+Yo}3O?rGm4<#}rUHaD>O9Juk`Q!On*48y6wM;W*pa5Lm#'
    'Ps(s#3+X+>;W26|z<suoGTH~vQq<1M?8d7|eLKLnBWkT;Q;n_*;g{;`Z>#6ZTD_d!dj2kOPi5>`6a!IPQ6-&#FY=26C#Yk6C2%^~'
    'v~hHcpULK_#%QOmtFx3by3W~Q<aLm{c?Nu~5wD$(+8Vi6%x2?clbF2|;@V#`&&0l`6t?PS?xgTL4=Z`Yyy3xIJ-(XVXYuaaOuNeq'
    '<F1Zp*Y}R&wY`lL>k#M2>7XOSc3h_%+|$Mo@)r+=sju4GP<c#z<Omp7M6DUI9Js)9_4qVWpC7sz_U=AEiF2p-{I$664Oanj69OxN'
    'p_AVQ^CpNve}()U!X{s_H!P7WvF>|LIOa>?vx+!*!WNM;;H?Uk6Bqp8_A6gW>bP}lTd?LBdy@p~k8B2vC=Re^ZLn_dqmHreg#Q)a'
    'MSbJ>LItjycRaN(BfgqBkm(%YrN3fsdI$~p3_ItSy$n%jN!z|}S@P<WUsd3~?64MbIO-<9#GvL=;+7VFUvh~b#UXHgvZrLO1%9)a'
    '!jBsJ+py@!aknEaybk%XK`z$JeZ-ks3J%u6Ra#^KUjvqg1Bc%Ewx~LY(}^RWob`3FR`~ah>n+O!Zm%))3rC6#*ftRRVP6Y)k+-O^'
    'hf55AuPpX#33<8VV5Bhcnk23Xe+`Zwx;3uP<dg9Eo#VOR^cSW&#8YR)9sBci<epL=e1rO4`^6eHAYy)fZ{(&}i@4{}rEbud{ChQX'
    'J-4-HCEkA+51#L>;S1LRXX`5B)SEgsGhbq7I=B1t^YIY%9-o39_{N?5+OBntlgl$vldH$4sHe@qlR3-eW9$ygKyc|K33FXy-WzIe'
    'cpwZ<m41f$`vI(`VOG~1_NeV{{)$-N_W}LaPOtbHh`yFnze0U$9&rKHbWhT$cT#`2-lINN=M?L9-#$Gj{IofQa3-PGrC}d>LZvfK'
    'M_{mm?b}5@{|dXrxug30E&R;HKIoBA*7=CjT6^S#Yv&2E%YDx&<K8A~$HYvQp0uxR?bLW4SiEI_-`a#K@k*3XtrL$$1*e`bgL7$p'
    '5-PrU2Fy#?xAm;iZ`5Pf_hPXebkH-vp9cTRW}B?ue_e{dIR{tXvGKO%dIC?c^!!r))VpKUDdK>>V1rLk7gwLe9^f6bdG8r(9)Gju'
    '`M;<?vDXLwI>8S+Tg+}a-Hj{c_c-zp3#0kJ<{k3$mWzK?lSM>Yu`3IXxaGiWU&}gM*83ah7B~0vnmY(zP0fAW{|r65Z?ECtTlu^+'
    'PRLIzfv@%DRN%6)Rf9Hmc9BXk(F*9^C+Iln-9GAf%fDws5%<OP^dA2Vd(4nuwUdTz8^D$JHvVvr8C>~EZng~Ed(CC{0}g7;-QeJP'
    'Pr57g>UpB&JAPy2n6wei6?by8LcjW)llL=$-A?1HCItg$=c7)cotAYEzrkGlhu$m~(EOEuuKR9dH?&hKhwc#lnU|jGRH2AH^pAUz'
    'njZFko@bYsL&S42J5fKye!%P3#q?v0-uo(PO{%SX@esE4-X7XE)pHlHg<K`)7OvlMbgVJda9a+YpjZ`Vn!3(v{2lME{lLegq640?'
    '58#ywHMecF<h?lljPF;_;i$Js*0Sl-z6~aOKh5twO>l$TD|YVTk=6=Keu(oYydy4GKDxx`k|)wf7aZ01z+KaKd&c1St3JKcyF<jk'
    'g$3f1TJI2c8{L>LBhR53HX(cOYOcA4nNr3aVL@wY#eLnUwffF1e`@!PyK5d3=nLrsE(vGVt(I-)sPp&j|B%1Ww$&K9_(<A==6TpG'
    'M+NcO1al`ZX$~A^ojIL_-g}^TqN^QALeHW9sgDB}(1#iDFSw--d*TDFyY6#a3!(;`GE(NB>#}dtti!1vq2BjlC1%S{n(3+=Y5pHj'
    'ua87*@0^1<9rf1giS0TV8^Gwjxy@~6mEx`4-!3&gXf%FbKgF&Co)WS6th+yR<CA}HZgPhb=Ep1l`-Qz9fzN&Si2j_Sj(uoyoIN0}'
    'd@cmG&Re0GJf%HfT;}ZwW+opq<s}ahbgV!7gs;!~>Hlaa`eo`X&iQ+OJ7a3lTYc)mh}W^6%atLn<1?Gd&{aq1=*u^gc`|SIFuVTh'
    'dvC6NpOxZU&#k>b<NI69EI3KM^2ozG*SxQ5=9o55f%EV6XrbK^=XvwJ?^5T?(4hf=UsYf=rSCw9zxc)k+#Utr2~Ev7^kN>kRw}TT'
    'Jth-H$KIT3YYR?89YJ4HO&X3wy%PH(7fi$@&N+Q+A)UK#dJf_ugA?IfapyZ#^5>sl{{0_|3Kif'
)).decode("utf-8"))

def digest(data):
    # Git and Windows checkouts may use different line endings; all checked files are text.
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def safe_path(root, name):
    path = PurePosixPath(name)
    if path.is_absolute() or '..' in path.parts or not path.parts or path.parts[0] not in ('README.md', 'apps', 'mysite', 'static', 'templates'):
        raise ValueError('unsafe update path: ' + name)
    current = root
    for part in path.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError('symlinks are not accepted: ' + name)
    if not current.resolve().is_relative_to(root.resolve()):
        raise ValueError('update path leaves the project: ' + name)
    return current


def download(name):
    # The reviewed update is bundled in this installer; no network is needed here.
    return base64.b64decode(PAYLOAD[name], validate=True)


def inspect(root, files):
    states = {}
    for name, (old_hash, new_hash) in files.items():
        path = safe_path(root, name)
        if path.exists() and not path.is_file():
            raise ValueError('not a regular file: ' + name)
        original = path.read_bytes() if path.exists() else None
        actual = digest(original) if original is not None else None
        if actual not in (*old_hash, new_hash):
            raise ValueError('unexpected local version, will not overwrite: ' + name + '; ask for help before proceeding')
        states[name] = (original, actual)
    return states


def verify_prerequisites(root):
    for name, expected in PREREQUISITES.items():
        path = safe_path(root, name)
        accepted = (expected,) if isinstance(expected, str) else expected
        if not path.is_file() or digest(path.read_bytes()) not in accepted:
            raise ValueError('required reviewed file missing or changed; will not overwrite or install: ' + name)


def apply(root, backup_parent, files=FILES, downloader=download):
    root = root.resolve()
    if not (root / 'manage.py').is_file():
        raise ValueError('open PowerShell in the project folder containing manage.py')
    verify_prerequisites(root)
    states = inspect(root, files)
    pending = [name for name, (_, current_hash) in states.items() if current_hash != files[name][1]]
    if not pending:
        print('Duplicate navigation is already removed. No files changed.')
        return None

    print('Verifying', len(pending), 'update files. No project files have changed yet.', flush=True)
    downloads = {}
    for name in pending:
        data = downloader(name)
        if digest(data) != files[name][1]:
            raise ValueError('download hash mismatch: ' + name)
        downloads[name] = data
        print('Verified:', name, flush=True)

    # Recheck immediately before backing up and writing.
    verify_prerequisites(root)
    if inspect(root, files) != states:
        raise ValueError('local files changed during download; nothing installed')
    backup = backup_parent / ('EK_code_backup_city_nav_fix_' + datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
    backup.mkdir(parents=True, exist_ok=False)
    metadata = {}
    for name in pending:
        original, old_hash = states[name]
        metadata[name] = {'previous_sha256': old_hash, 'new_sha256': files[name][1]}
        if original is not None:
            dest = backup / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(original)
            if digest(dest.read_bytes()) != old_hash:
                raise ValueError('backup verification failed: ' + name)
    (backup / 'manifest.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    print('Code backup:', backup, flush=True)

    changed = []
    try:
        for name in pending:
            dest = safe_path(root, name)
            original, original_hash = states[name]
            current = digest(dest.read_bytes()) if dest.is_file() else None
            if current != original_hash:
                raise ValueError('local file changed before installation: ' + name)
            dest.parent.mkdir(parents=True, exist_ok=True)
            # Write in the destination directory so replacement is atomic.
            tmp_name = None
            try:
                with tempfile.NamedTemporaryFile(prefix='.ek-update-', dir=dest.parent, delete=False) as tmp:
                    tmp_name = tmp.name
                    tmp.write(downloads[name])
                os.replace(tmp_name, dest)
                tmp_name = None
            finally:
                if tmp_name and os.path.exists(tmp_name):
                    os.unlink(tmp_name)
            changed.append(name)
            if digest(dest.read_bytes()) != files[name][1]:
                raise ValueError('installed file failed verification: ' + name)
            print('Updated:', name, flush=True)
    except Exception:
        # Restore only files still matching this update; never overwrite a new
        # change from another process. The backup is kept for manual recovery.
        for name in reversed(changed):
            dest = safe_path(root, name)
            if not dest.is_file() or digest(dest.read_bytes()) != files[name][1]:
                print('Manual recovery needed for:', name, flush=True)
                continue
            original, _ = states[name]
            if original is None:
                dest.unlink()
            else:
                dest.write_bytes(original)
            print('Rolled back:', name, flush=True)
        print('Backup retained at:', backup, flush=True)
        raise
    print('Update installed. Database and project media were not changed.')
    return backup


def main():
    print('This removes the duplicate links inside City Information and keeps the top navigation.')
    print('It changes one template only; no database, media, migrations, routes or JS files are changed.')
    print('Stop the Django server first. A backup of replaced files will be created in your user folder.')
    answer = input('Type FIX CITY NAV to continue, or press Enter to cancel: ').strip()
    if answer != 'FIX CITY NAV':
        print('Cancelled. No files changed.')
        return
    try:
        apply(Path.cwd(), Path.home())
    except Exception as exc:
        print('STOPPED:', exc)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
