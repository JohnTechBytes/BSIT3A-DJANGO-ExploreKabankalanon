#!/usr/bin/env python3
"""Show only attraction and festival guides on the City Information page.

This changes a reviewed view and template only. No database, records, media,
migrations, routes, other templates or JavaScript files are modified.
"""
import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import tempfile
from datetime import datetime
import zlib

FILES = {'apps/info/views.py': (('d3dfdf3aeff03bd8683ebdc53760eac4d368faa0b2e1d23215dbc904b683ab1e',),
                        '745d8f2b24e7b2260ceceae3f236a130fa4d7b7c6af972224dad5e3839e80d37'),
 'templates/info/city_information.html': (('715f0d1f38d730a9c1ed3dd3c74fb89b7c60325bba7459ad6ffc52365fd64378',
                                           '7abdfd1ee5b68f6a99b31ec65d90a55079e40fd1fc2ebd4471c3b1cda9aa3a76',
                                           'a466db62b977e2e53d75054d15155f848e39f31cdf6d9eb34105af0120221f36'),
                                          '4b280087cd9b9da62b5bcbf169bae6d7f58d94ab36027be8bc78e30845522b25')}

PREREQUISITES = {}

PAYLOAD = json.loads(zlib.decompress(base64.b85decode(
    'c-pO6U6Z0%68$gz+8Z-~MR&0g^H6AksAVZCUoRU13Me4a_=Ow$-}mGN6x8mS+1Ll86u9^1%{+PX<fZ=oWtnC9?@_wm{eFyAr~J39'
    '`0~#$TBJpbz7e@<ycu=n!ZDTY$dnFle;Z7Nm|M-{ftxr-FX2O9jgM|5r@k3)9qS`-5~<MM_o1CAhozw8w)t}C2HD(KmBfkU4Sok+'
    'N6%dK6u72xuuVVKR3&%2a&KwrqV^siXb#-tmRM8k4`N%83a9@OEHTzsLwbJen(<+2jX5vDbCwf#Q#o`KBOgWbVyVU#tuKd;um~J{'
    '_tbN^f^DuK=CJ+bn}Zx<caAv?Y)hv(Hq|~b$24#-pPNpPPGVeeU9inl;B<`4QH{&zDa-t>ymbZRqN(DMzB}eQ_SHpB`|wqxfX|Lz'
    'B=c@6^LBF1JRu0Y#Mro<!PYBYhUDLF;uNmH!M+S@`o~eCN27#4VvXD@<jl1&M>>VSCCoF;HRXNiq=Tb7lebIw))8J0o)F?0edAj?'
    'Y>D@tDiuD9mxx$s!+H(dl22YCZs6YxF*>-av{?%9b7P(PyVRR;#=FIh2Zj=_7w<Xtb3WR_K6Vs|#)?0k&y>gqO&eG&5%<JPq`lS^'
    '_pYGFE{h?5f*&~TeVqCIxQ(M=H|)l;G2NaAQ(jt_hO8`#H%aS;Y`&Q(CK$U%%raMaIk4ZnE_&+XFg5hWVypCw_jodoP9;tkZ7hwp'
    '?Dt}2$?<4wnEFCo45wH#(PP3Utzil6F+<?bvy9m5Ota5m7iitLfaM2#?-zd=OIQ3bZ1l-~F?7|lsP)IOZ4EX{)!1t40KfHk)t??1'
    'Mk1`$E$z~JTu{c%*jfVlZo3=K7|xh)Mu`+Hfib`T0sCWy!(m_kF<G1^Q*N*53gT<%j>XHP;Y>`H*5KkJK-C(sQ7@JzFpYJd`tI5M'
    'Z<RmjqcWQ$oAJXbfKS$5$srfo+r-cd-=rL2^R5y5lVeD0<g~O<jPCqB?peI<EZ&XzsG1l1%j&pjlo!b7KeNqEq=PfVzUo*N^2AlA'
    '@E!P~^8x;NEjgsGciaNGV(H=16l13=bA$`z9_2joQ3qK20X~_~^YAmn9`Y(+w$E66hvoi1h-Z*@V-C-V#67?Pp4DS7{Qxco;H)@>'
    'Z3W?kaTfds8+MEj2}@-@;`)NPV()ewvS|aHaL8wFRPDzTjGWeSOuh8sjO7RRq3{m)aJ2Q|O)+(>=}t>oZbT(c-him>0o+?Gt+yR;'
    '&*od2_LDi~gWH)hzP*plH3#Se?7Axaj`&&~wpK8iVV#?;@WXg#b;z~>!*C;?4mxKnMu{H-hmkkaG7a3Jbv4*4Ui|(b^MFtDvO9nD'
    'WWSE5&G=AfI9;8ZwhWFwpGQl^2@;E?7IWX~>%J;+;PJ?sHZki^{uFM<V|yh(dr1roh~WG)Z2s73NdvF2aRlx~9698AJnZX7)U|xF'
    '7$1F%9d-wq)77%tx9hf#TfS)dQ8f;<U#g#z*)11GiIchD11}1O*JrEGViuzA>3Nw$<0HlpjxQ6d;uA$W`=(K>X4_!hmGz;Dd4w@y'
    'FSDGncqxM~53oOT(+}z1zG2f(-EFzP8YfR;{;lMY@^kYcaCzI;jWe40Kj$x0JME56HHO8E__&N`T{}bM0nLT)o$0O-Bh(G-DVCzu'
    'ENI6a{I5~2QI65~RQ>_%*IZX}wmDwg$UFQkZB_D}pP+s-jyglX7&-C=Igfn5yG|VTw0=b*`)x3+pgyYPW6}xaHz#!aM$E=4cQuaZ'
    'D*yVxqH!XQ01n(5t4vch{RVz@RV8wuO9;0W&u&l`cCHX_;O|yUfRorQvE?%VrQ2#w79Ww>)bcmuU53NeOw4Fc*ZiJyLDSdme8N7}'
    '7(BvXTKHxkIfWMBJ>Uj8bi&_*(+$7Z9Q7H=&2@6EJAif^#BNvnR{MR_eT%BSu;+oNz1QKcTo2yld~3ioqf6L`8oWqj$?igWTIWYe'
    '$hqJL)aUO_-)U(B?`7Skwb>k_X8r39uKTluEAHvp+rHb+m;N;*=t4YS?lX3yu&F7syD_LQdgv;RG5s;`&cgCH>R*Xf<1*}SAI7qH'
    '31|3uf6+F(z&t&~s2Puv180;=749*n!X3q@VRy-Y$VparuKCh?%gFCGY71#}8eiRGIC`i%7Wcq&45wA@AT|{yfR*S;9yj-+aQRQ;'
    '*tzcUfq(9NhWko^`PZywrQ2#u>sqyrEP=cJ`0|f0`&E*~%l)cqth{Jn{ENQ*NS6C(m;M&+lNeprsz7&Qg;d?q6}&~HGF)?Uyk+ws'
    'gyK0Y`}!VP5DefQ8Uqy=B15542)Q5E>&RZH^&ILZ=3Hdzz~Y~GR3F2R_HMkOD*|&FBX|@_W)C&09GFe8r=IJ6Zaa~-46&+mfz9#S'
    'LPn^Iy`w6{vZ%7cr1f6W2`DL)M7%8cEzrCnMFVf`t9@dfe7~g3NW^$G<4F-gG37C_lA{iCR~Y}$x`xzE>00%>KmLIVwq|OM)}Nn4'
    'pf9(r@nteYw7UESoy|#$<Q?{wOlH~!`vzM0tCG?-;+#E$>P^T+7Lr1L9SQGW|8)N;`AT1xm6Om<KFArX+XAu$en$o&bNP70OOZ#N'
    'T36ipDxYgn{p>IH2StJmXH~5ni!qD;Emny6kt#0Gj!u}eo?)UjM_I+Tx%LhP+!-99ekV3q&Y`_Q+5G7mz%T4v+nw>n5|o72qdiSj'
    'S}!L?&M7X)?%ZLFW^lLI489L$4IB$&U`o0W!;efIY9v3<yaS5!O#9Q=P<OR7{e#sRi%_|-J7f3&Lx?|EMd)!6u8S@`ry5Y5TCl`*'
    'XTwD_5AIPF-)LQb<8?lc*xL!YR!}9!@09JUV@n^Kw_?0`hbp!AOY@xj^(h2$%PY7u@J0Kg3KX%9jqHc2Y2m1epXu(k#Hd{6)rAAY'
    'Dy$lgEOv?!0bg7AYi}dBM&=c>(S#~r@4TZE8tP1d!4S4eT4ID{wc~eCb4P9SQZg%^{g{hSd12C(aPRuuX|mO!2EgnIbt)}&(8dtr'
    'hiVtv9oCfxHev*f3oO@EpI@55bMf*z>b!le82Od0JA1a@O1&aBF0cXxMf;|z0v}YJbrmmEdQ>5wjr&ZP8e1>hCj=~J8Yz6?95a4k'
    '%pH_|D_Q;(V@|#`ExWooFj6UDj62xKV~jg%bv4BORVRP!Z2CN{1H333#|)1yscqP~sOKuX<DhNdcj$VX_64>7zOO2)q{X!l>dyC$'
    'zw21yLw<PP!7=P-bOPm9oh|mULoBwA`GPgY5F9Mk)xNH<l#{FCu`06t-Ea+c$Z&i0p`Ai`sdQS$=EJ;W;DyhSV_$0@0AG=B=^Wy6'
    '#lc7*^~|x~gue>MU%Mr)FSIAN=Nrezc2!^M6BYO!^T*-HEL95fduyj#<N)*e^|_H5Vl4cgcy->OF4@m==DKcc%!WPxb<%%(HYQ$~'
    '1~^;lz)$R?MSJ&+*+N$qm($Vfy}T}a;2U%LYrD23PU?FsCpRyzUQet}Q2Ex06Lq50H6kC6gyET>Ky8UXfYs2A%ACU-rQOwE=IiHs'
    'pc9MmimyJaYf0TDSVF1t(0NN*)%jkpQ5~z*R)7Ef;XdJ~%^`%dwwmpqPrzUS+p|@&_y)V!x}#ec8L@fFuKgaTrS?b&*TyS+m)Mq('
    '`@LP%_K6m(E$&b$wi3_iXj}Fx=%PBrD_%gkUUp3Jx;%N9()hp?Y<90aRXDfqHBY^s`C{FdQ8U1wYW&Ta@1m+B%Ws|S6C0a3*JF4Z'
    '()~LBsdoFwQ~2R_l6Tz`n}c<-<#TW4X~!?ey#0mzV{_f{*BSfJqt(2@>1Ns0jx6}1>TpLT@6bM*T>Pt?EW4;K&p4vVf!Df*j?n4-'
    'jdjz;^}53WzN(zNpZ@|qduWd-JKZ&PZHdo;uch^j;j*$-tU6TkiI_t7zCy=A?<&aOEdGqD4sdq9`9H!ObHukJhi=;jaHXF4ch?*>'
    '7Jd>NI*Iz)>VTR!s7?WHICwkMrv!s1UDyOMCT&E0#go`<P_G_ia$B=`n!qjl#@<GrLOZR?8s5NM`-9rdr_lU`eJSg1WjC}_$h+nM'
    '^*PS1j#0SG_s~D)nX78pZ9O_Ao0a!j??m+!^8v5lR<nB_-Rdf7P0Foj{$RHCKEAeXD*G;A3$Y3=lZO+KN>?!qRos@ePvt87ot}=p'
    '<Ks~(gQxT(c%?wjWtEnE=EtA${RTQ5`8JJOHa*N+VY2tr_&(DF4cuO_^9+wPmSOVF&kuNqU#@&q`=^c*J0+-aR9*vj&2IKg=q*dF'
    'PoLCo7yfTyf%v4<JA~c)jz1uKpK7j!h@O&81IN%>V)|V7iLJUbPhQ(K<LQ`}0Q!Qv!zJOYXlmJZjO4#>|6TkZZL3cV%RQ3zDBsAA'
    'c`qH5Z@Q|JUV0NtYoYcYt2ZdM{toEATfV&lE}##i^38`WD6q#rmM4_eJgqkltbb;2f*$fx(W%#=x5EW{gTdb9JZh$^ZlwOdPqp4-'
    'zJ0O|`gG)5t0uPdV4?z}&-ymA>Q&N@c73aJxPO02&wTNyyC1pn)qd7DnF9{}<CXvIR6mTs=k&%yQ$ysj4NZ=<`^1%RDZ|z!dwLRD'
    '_uEtSOg4JTIu0ImtUZ6g*Q0*=KiWxe?&$>mGimmiBJ`F*H5mRnm3_G|z;FNJ%z5al6LfTaX0iwt)f`&a-hB2J;^#bPXFW}Of5!Js'
    '&CEEdbLEk*H?FyjtNNHWPl5BF)o7;O;ph54E$TdXREgd~vNv$RD!oahvjTR;1l*n&-!V<?#L$b$(i~TBA71Fc1?Wu+<yQ4(ANrbd'
    'QZ+cLm6#W?aF}2GB&M?#(z%DK=D;sJI1zhGpPW+#fBf;~KmP^25~0u'
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
        print('City guide update already present. No files changed.')
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
    backup = backup_parent / ('EK_code_backup_city_guides_' + datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
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
    print('This keeps attraction and event guides on the City Information page.')
    print('This changes the City Information view and template only; no database, media, migrations, routes or JS files are changed.')
    print('Stop the Django server first. A backup of replaced files will be created in your user folder.')
    answer = input('Type APPLY CITY GUIDES to continue, or press Enter to cancel: ').strip()
    if answer != 'APPLY CITY GUIDES':
        print('Cancelled. No files changed.')
        return
    try:
        apply(Path.cwd(), Path.home())
    except Exception as exc:
        print('STOPPED:', exc)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
