#!/usr/bin/env python3
"""Install City Information in-page site navigation; no database changes."""
import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import tempfile
from datetime import datetime
import zlib

FILES = {'templates/info/city_information.html': (('4b280087cd9b9da62b5bcbf169bae6d7f58d94ab36027be8bc78e30845522b25',),
                                          'bcde7c8decbaaad9dabfe7bf0ca98ab882ae6fe25a60f714472673cf6ad7fe5c')}

PREREQUISITES = {'apps/info/views.py': '745d8f2b24e7b2260ceceae3f236a130fa4d7b7c6af972224dad5e3839e80d37'}

PAYLOAD = json.loads(zlib.decompress(base64.b85decode(
    'c-p;L*>a=W75$ffbyY4P<2I?f4?+Wimas;qmlT7{paW7`Bc$^0S^I!wNmdUxmCA$5mN>&6)?RyU{I4&&WxiqlZn^y<E#B9Egz2vQ'
    '2mSRu_jl>K_*=5e*_Xe6S(b~~a}vR`<yBa=(@0BLU@s2gz)Ay+WsYPdp|sfhgXu2l=&|7l-)K*uDT&unt4Qk$zCF5p@8+k2D{bRQ'
    'V?v-U@V(geovEz%*xt*PGO%gAve!r7T6)iV4z<%E%&nno8%dDwl0fV4xlOR=eAfNhZmz7BmXcv@1)JHsV{RgCvGcTk>6dCo_YG~j'
    '?{yby{lc56%rC{2@0eN8@>p1`c8#C7XS?%rMGSM9EoY+OYu3(lwoKQoy{8%5Kr+AU9ZTsH^j-6LV1D-<^&Roq`*i>Ol<1ndbse)B'
    '&y33Jh?Os~qn@g3_?C}ndIrBYK`Lf}BvY&fJ(K5r&0u=K-a}AKSx`(~hf?q9m;M(NtLeKdDf<X^MjeU)*~j*-bP_$pT`#6<&lcHG'
    'RMIf-@4b$^jx=$rr{}dl@lW#(L2JrFcHWCUi~lZH$oT;_mQHJ$c+zPT<Qx+>XXriTZ?M|xJ(+ne;}DkW*p<wUN4{zO?Jw^Deqrak'
    '+cGOh>gRMH`83w(zHJPfx0IJ?z_y-aA}*HjksITyF}uRCWCBx41q`vFJx#)VyQgyv%JWSBWo}?|<=fHTX_<0}7zQ(rkF9UZz>UFz'
    'u8`t;IiPi##Uj*{kMF%qNa-9rOHezR-iflXH9EkzBWkVmW-@&)xL++-8D;I#%zCF$*WLN{X&X5v#emmVSPCcLi~M513F=tMI8G-U'
    '`mXt`9$h<Puv1vtC&ue&vVN^?TRe5rc3o$<_j5h9_a5On_YT9R_JX`G=>zhgRlrHIoNsdY`21F?{P)m_O4n(>L@n@17we?{@hzJk'
    'mz{Pw8mP1mSYQQe1m{`1u-ar)C!V8!)in`$h&DmCKI+|eJj#sY5@*1c74F-6)%rOc#PO)hxuHZ3%Asu>BGgteU!Uk%C@ILnB-X1*'
    'WzKt|mu+MC8w2wPZ?M{j5)-_cxN;ri`!Kh@5ADq%a*Vy_T(|<Y#RPCf<F^VtFJi1sklQ>cMIKMRBQy6LtNP5n>$tHyQ{l&S6Sh?F'
    '#Oeim2ou1V2TaCz*549t5NGg%SiR*YBTfimXMppDcEa#{9d*}&S;q@pf_lu>nK!rCo3;>mtidmolV!em8O==|C)6M~LTq_9EBwLa'
    '#mw4AtQDwkfN=&ML2jm-Kze=&u-2RZpJOxMtT`{I6eDmU@cx#LWH(<tyOsMD9Lbi03HaRte;ZUEhalUCz%~nW&MB8Q5o*(Oj3%~9'
    '?iD7Zm;nP=BYe|4z`q1M7uP*QrvC8Hpk<XoZplNZ;m(}%((Z>o{HzwVet>vw+?kjmRwZE>TvMOHgm`(Czc<@J{zejVlEOdOukV0k'
    'A<~rH8(|%N7Hc=);p?@^RgK>8)x)0l%R2s)v*t`WiBdIr!y30`RYS+yAa^PCcK84sOnI!|GV@1vUe;XYqdMnf+)-*?o<Dzk#I3h|'
    '>Cz|pvoUzVx1VG5yae2+==XR_)r|+f{oH$>frIvIou^CReuT|bCw$nw9r{%2*+)fRaZJQBx~FCAn!1VWJu2t<u+%w!(jBP#>pp{='
    '9MNNv18RnIIe1zRB#|Kw$v9rqo_MVFZh8Xnvqe8ZALwVEGkU?D#Pu1k1Eyra8Db2+=!6uPKcEi|QOjgwyT65IdzxN)h&pM`;5y@{'
    'HWE+SCIb&A;L#F)^WNe}CNKtUN!FJ4#JRFVJ>f3Yg=3^k^vF5#5ax#b8$NODz41C@@BVE}>-YeBVa}4FZHi%GQ0^7I;8;z^k8^S5'
    'n@av{yi_ecr!S)S3&X;yP+xm!!FSiOs5bW0Z?TtgoinNJ{f)R(uH!MUublI8&gYze-+378SnrZnOuz>&`~bEG;G9mopq}YU7I<Hj'
    'otD9(oUy2NIn!Lu)R~9c^PH%<j_bK*eB0$UL3R%%)NF%s_?J*We1vm6D}yVn`rY2sg!8y+P+r1ZY`FG#pl9cGVOQ>5v~;Q-BO83n'
    'b=4%EN&VDC4Y>9x36Q&M?4XvQB~|!FnpG_#n}O>_d-!wwzzN+eJgVsmTvfVKjG7b~`p$uB+mpDKOWYRE{Y^~yKIjPIJx98oKN>v;'
    'ZK!~Ipvfe{thsKup|OSSF$W3gEpn(WaJESp&wOY$aL11C!x>TD-$ph)-+|MbHGSn2*;a{ID*T>0ziaR#@w=k4^I7%0LfZY>zUOr('
    '|G+->)*5!+#2~Kwt-86%Q>uU9Y{2J%oa}-A0#{foXmIj_aPo@S93y8EqwbF6hp!<Qs0G})chUQBm#}nH;!p{>6lu+}1<i%J_mEG|'
    'p1$+FwSP|!aM;Aq5V;OZRem1V;kL2!ok==A$Dn&WxP?XiZhyf+N8vTiKjZls$N0=~4LfT7OVxS~tbm1cFS8@jhpqt+$4w7L&4N3$'
    '6T{3S!-l38p4W-MZXdSG#kn^?SN@<kobSEa!`F|q)A7+B&tZ&nGHPuiu!TKS2iAi1rWUxN)qWalG3t}8er}gs&(T`*tfHFKpT>js'
    '(}HHJ+}$-ZJIxg<U6X0<s!(&#6u@wA2MqQ1zSKu7p6i-JUDtLuzj>@5`w(Dea%cKIuaZVB`7GYzbEq<&sRCxlB<NqhyW&*!D>TF1'
    'bHdLphY-$y1p&CD8CS#|uc#mJFEp~VVQ;BX-#a_;-@Xk$Q+^IGqsR9+t!qW*xPI5b^Lbwkpo8_*O-xdKAS%NfUOiRb?8g4NuPH5_'
    'j{$0(ddI*3x0r{BbOrY7nv(Npz&y>aH_ryD2yFxXlu&>89E-u}7=XLrH`niaUY|d#?*aFZ9@u!t{lHU)o}cSqi%Oh*q&SfF0iT>_'
    'y^k}%JLh%8L%-Vd8}(P8b;n=ep_N;#t~tHnTB0LTESkUNns+E(S6uwFnxuCIk<;FBj_6!*VCUS|Fk{=3zi_X7{e8_HgwuIlbNA<C'
    'rb~j`J@pLRIst=n5ovM!?g$*0jjemq)`4Tb2J{}LHC?|CRLt-O&A>0-e4X;R7pv_@{B=45`8A<!pKokHEw6mXz5NceX7q#HAQtJF'
    'XU{($IH)mqje}uc&!qf4(XH=X&xFNvgMQ5(<;Ioz<%67D?j-CszCwp3VqhDnQ?_+lyoX<7?&b%*dFPdC73QP5?>2T1i|IPD#T5N{'
    'gSz6H4RIqKzm2+e5Bs>Uen(k9$IM|vL*yZFa!QuP>Qjt9`YOFULv1~Z2e&P*#<w;B4=0W-<Z3;tZgBm9qb|o#!)-Ljni+C`Z0d~T'
    'FYG?rd&kE!`3Rm80#U(!3)q<4^yItzJ>+{A8WcVXO)dQJ+!~YZALjRwCb+`w1v?M%NV7a)@-EJw@D6=&;iEHWT=E2clr}i3zuSh='
    ';=`UUIR2tfA8?B;9x-EFV}bbO>5Sd8Zgg5SUr^n^-iMk?d<#mIW|Yh)tyezQeK&n)As_B~#=|}O0JFj!E;-Jwwd~+FM}OV^yZrS&'
    '+16m>>?3;eV7i7ryuAO=HE$CPpk31E*y0@1-=qJnp@%Pa(0d%x|J26`7cQRBJ0|1?8rLeI3FWJEzTMRT3t;=_x>Of5>%bP=v4D1e'
    '<?mTPYo@dALSF{AP_O5)?L4?ApQ7Gwd*V$UbWeoQM{`UwtH{-Df4kIhGv_4lp<~hiDtIhD>+a9oNHg|>`_f2zjz9R{5TIRgPJes%'
    '4!n6c!Eyh>HIt>>%@_Rr0?pl9vhk9K;%>(Mp?>-w+WGtMCsKTFq2?9nsxA1ezeKMEj+owW&M4ctUd7_ueD(Euw*D#Kcds;a%}Ey?'
    '8DI3*)xKtqx#OwVu=A)#lXhQVKC0^rJ+$Gc=>ZxL_*DeLs!MvIfS%=ZAo9TP<C<DREpNP>zt^C-nEuCdz}XwBEgzf)|Dms`Ca0LC'
    'aqnOhL!;$9E(89KPavH;%<7&4|8~TQ<9PGn{|f6rzx?|@&@ZdW'
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
        print('City Information site links already present. No files changed.')
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
    backup = backup_parent / ('EK_code_backup_city_site_nav_' + datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
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
    print('This adds site navigation links inside the City Information page.')
    print('It changes one template only; no database, media, migrations, routes or JS files are changed.')
    print('Stop the Django server first. A backup of replaced files will be created in your user folder.')
    answer = input('Type APPLY CITY NAV to continue, or press Enter to cancel: ').strip()
    if answer != 'APPLY CITY NAV':
        print('Cancelled. No files changed.')
        return
    try:
        apply(Path.cwd(), Path.home())
    except Exception as exc:
        print('STOPPED:', exc)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
