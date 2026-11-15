#!/usr/bin/env python3
"""Remove both City Information category navigation rows on a compatible PC.

Only the reviewed City Information template changes. No records, migrations,
media, routes, views, other templates or JavaScript files are modified.
"""
import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import tempfile
from datetime import datetime
import zlib

FILES = {'templates/info/city_information.html': (('715f0d1f38d730a9c1ed3dd3c74fb89b7c60325bba7459ad6ffc52365fd64378',
                                           '7abdfd1ee5b68f6a99b31ec65d90a55079e40fd1fc2ebd4471c3b1cda9aa3a76'),
                                          'a466db62b977e2e53d75054d15155f848e39f31cdf6d9eb34105af0120221f36')}

PREREQUISITES = {}

PAYLOAD = json.loads(zlib.decompress(base64.b85decode(
    'c-pO6TX&+$w*D{cHDl}r7}g5=Eowk)V;ha!UiRRU2wI@0z2Y9{zn^bb0Rn2$dyn(bqa#pNv*!HfH!oHH{$ux%ZkWIO*#4PhpX)!v'
    'WS9So{`!^ryJVgHBi^O#kAMF0k<S;N6HA`0uEP8|iHw*9_WTeItRyhl(ou$SsLc2NV7d!>=3?kbKWI!~XtCGp#?fG!yY^V}ZEf##'
    'y6d1bJ%oAp92q*Ey;k45>FMAq+eKtBDKO@EF86(Bs+uos@1<HE*gBuXeErceU#!Q_I32>&8oBl`4$@s582X;e3OUQU+H<?9w)(KN'
    'CB8jlFYMD9Zz5y9^9()r^X`(?8`-qp(=Igh%$s$YpUW%X883s5$HHv2EB23dwmU!7<S<p)$4r)d!`gYymYIgN_l)5-P{zN^o~89N'
    'dRF`%jDPt~_Y->C`?UW1DK?Gq)^*0`$!vJ`dh*#<*wIY7YwRtZ%*-YBy$KR|87L~*Kr)x=JO5@dJz(r1$fhjF-kwIv%fq+(&q!C('
    'Pgl|Q5#)?|qyv(V?Oo+0d(gX?P1l|+vyrSNVXE)Fp1O_<d21%+w_ohf@D8vq3t2f9W9I*ztzh#5WXzq;H1?F!CP+CZ8grO0u-{;{'
    'HD6Tbb%uniiK~n^9_`K0x8JS-Ttm)Jw=+IFik{MXw5N$d>und1c}sSQ25jp&W9Y?_F18u|J)G5Wtc-yv?F<aDkv)yWbi1c{hh*oO'
    '`K@gr^Vzo}_{dldp~GOt@v-%76}TC)pf4qOt_Jj-VX+9l=Ht1yloFZ;?_&7Q((Facu=9Gr-j49W+?%QNJLCK6xZ3OTIUg@yPOp7;'
    '=i8@k<cvuN+_%D9Issp_F9w{zzqKXD>D#)AqdI=x)=vVXUEx<}De>rc>K#T-7q*)xz}E`;+PUzpkzHXnnJm@|vwwnK^_AzCnD-Pz'
    'R?SSU82e6xTwZ(5@L(<<f0(^z{_X3#dXpC>Jq_=w?~aqzbQ3D$LzKd%FT2<U9(_gMy7uD&c#K`eI-3Szw0p$<m!vz_K0*d2eayO9'
    'WHZS0y72Kme2<xfF2;`8Xn8z@{c4>w=nQu?A7*aJABqJGjMu;mcwxE@lsD`v;&v<fu)q*F<OuxmaewjkEsg6hOl7j^AxJ{PO9C7m'
    'z>S)jjhX8VmwwND=p~SYWEpTjPQft@7{Pw5m7_ohDgCYGAG7CpGJ8&3*qr<FJ20Mg<*3({KAbLtENkDMt~~n@_EKYT9OSK!Hy2T='
    'ZzFo1?f$;MPFJhr-M3wibuJ_RO~5sX9TNCU4V!ye1gXCB-huNQYw>S%?G)KoxkhP6==MbT(M(p(CAge;t&Wk$buWcIU>6pTY>XBD'
    '{SN%)uCgd?-_rdzI_~g&&>o+F*<<9qEx;E?+J_I^6Bl94y$epoT3pxot-ua4ee=-)&nVW`113Cs`pL(BtHYs;xC+@S+npnOxbq$O'
    'RH=jh@!)2b1e@%+pV7FU#_=lr?sx!?#E>t?Z_M2#EN;A{3x3f$juOeh0}F-!6V}gOf!kYn_c|8w?zydB=xOC<D`1Ipb@koIjxlx$'
    'U56zPAkMnCIG|d$F=olXf0zuOZ;fFewuKm^b--u+nKkvym&lsUr~3TN{rAc5gFo%JujN|tcZ>2J=a}W=Q`lGE!TYI~$VcdX>+{&~'
    '2K;IgaRy@4fp9QWboiV43$~7f<nd|Ld49kgLhj;!!q%NV5O2g4_m$Wq-W?28hq#UMfxe_sE<o|FdPZ@%!Yuhu>-|8+n63;y2S>&X'
    '9QgM~-jxu$<3LA#)S)#_$6#O~cROu9()nMIi?2Hp>u<2ngwKPRA0~V}>~vx-VwZ<GcrKL^k62I8UFtg4HtMgFrcTVorz7o!tX&az'
    ';9Cv(^)YhBi0rW-U!fc*%oyb`GGYjg2S2;~9k4E8-p0EkPo<c-x}}Rx@OtDRr!d%G-upTc^RKr2|C9m$H)I4adP(UQA|B9t@>lXz'
    '%0(jhCG>zeH_d$;eo^g-&jCL)i|?L!jQM)Z^KbYcp9|cLT-JWsAr@mVC+uUIe7x6UvK{5H?{VZn7e?`SCO8cHOiHdO*1YGFSxC8W'
    'Pv)_^!sun(`ZWQU^#6l(v)c1ia0lV5@VWN<XXNMm<`@S4l+T~W3HFI3!~k$8$7La_id^5?g&op~njw#WLi|AN)#1Mz_A?oBy?@M3'
    '7yT!g;~n<xbmO2Y1M=<ZCTczN45r+%&Bm+8>Rt;60&_JSJnt!w44l^n?_c;|&naJ_I_ZXOmf-(un_Si;jxYAAO8&swx$sluf}ik%'
    'Z3A=7e~52#hS-<8XA!pwxseOTa$pY;<Ji{eSb5MB@fp4-QH}!}T-I}@+akV+8j)f&<^x{;LXPopYwde+upwLj^`R+~s3U<b*lKZZ'
    ';QE52qrgzXZ7JfNGR{$>2|p9~JKh}I;^R>!YFqG14xif;x$!MM-sAfva;O!L;dPm=<}EPUziZznKehBUQY!4+!Xu64m~83!3h&TM'
    '#Yd%nN;^@`RpLlI19#0X@=Pe7>mbG|k2hm?0R1<xKzt(V5}u!kd@cSA9gAx61<8AzLs9LiqDH1XZj9Vk&ET6np7V8(2e}T(pf=*p'
    'd-~Lj88^o~E|6bHEnE`L@)}m2nl|eG=kmAgcP*R1NV!MKJ*YncndLAeK6^tQ&9+q6j*{-2)<Wz(&^KWv$6`V6gISm2IB<cw1$m{<'
    'xkZOO(SgQQ^VEHT`+&6#mHD+_>Qk!S7{w#_`#umopR1gy${VSlF`!r<a^2ooXYY}}HDY4Z4<-gMdaDk#d3}ev^R*e@YWaMtzBmZ|'
    'RQZg^+poFt$(`L=Zzv%*ulV21ruz~29Q7sQa|}OrQP*JY0deJX#<6wY@SMp}nl($=KX_9h3u@%j4k7Yb_x%cA*ZI@`qnu^k{4>=h'
    ';4T(EtRmmiDF#DdN6}|chWH(wy>}UT)e(7g*#nv{=4I{ObC*B+bM@!@miMme^4_g`YB@9Kq)x>n4;QYvjN`d=o2S}Xs-AHiP_Fq|'
    '^#=+)e#2LgX-MzMPwwVlqPCQec)o<6?nLbcz2_Cr-OV4s4FbQ3$hSC`EnB#!x}<l@#+K^YWDlxmPLnrDe>L^)>)U)>)<Qp;akN<%'
    'mAYuuMcKE#2CdO+ute`9%)8Vly3q$L;sehOYx7td#(~Eu<~dEf-N*~6F6&XvM|{-G`>XX+yx)Oq*5ITw)#Q!!s28IUud@B6$9%zT'
    'qxW--$0{$qnFAUuCmbS%sMG_CL@$?eBY_D^JGyqn5bt9T9Dq0j4pK!ecFASG|F&JXWkuhr(t#;*qRtp|JYIaM9^a7{eZL2aBlBd!'
    '#Jpu54js#+|0;Iy8VdPy`i2;%?I;$I-oyNe-%r$IJx9nB@eN|@ir3JlL2+YzKpwF5sGpj2yNGd{urua$pl@i2i<pFXf|x!%P}~#a'
    'WJdixaGlT-;w{M&WMdiJikjlo?B7*>FZSScc)xNVD8v7ueL4#2<IdZKgTAbX7{%lAcd>r)yoOVbcgl|jrQU$G=K2lJ<Go!)CqHE6'
    '`N?Ihen$NbKRUtJ#=j6dc7%&o-57`2bOV{$Et?W|qyE2e4afStcy3<tGI4A1%^r2Of*Ajax}cO>)CdOkqF-ur(RYYlhAz1?nfwm='
    'nWGjPE{pmgC9ZH&ed){E2C*+IYlLD<sZUWqlzp>8j#{pt)a#Qwa_)JZL%oXxxE#C{J;uUMpsNVFF5YhgMer@;gzh$Kv#u&)ZVf}D'
    'RP>xnTZnq7=(pNodq3h_De11@!|})&#~ky}QJB68xo+84$X1Lg)^&v3g+7b<oAp*r-{pI;J}Y!?X}lNB^=RnZsQ-nY!Hq>cfFGRV'
    '55&I7{oL>>w)weyv3V{RHa8z82HSagYj1YZ$1ibJ_yhEHsYOx82L^HyWmn-*$l1hVv4^j0{yVxCxLL6+xb{rB5av~&XVl)v7Zn~$'
    'N}O*^16<j|7>q-nAk#TRXvE;pr>b}L+d5ue$C#Ebi<oIX%*!>18wZS$3{i@_0J#aRar_l7X7w{5$0LrwUaX8b9==rIvESR}-Jb!t'
    'kn=0JF|u{|kl-WAv3NfQ+)8#9`N55R{i__kX6wfJ(D!w7<x3acn-5L@uj-gRKVxuCE6?^~iaS4(VZUaxJ>MhrN@sDXPm+5*fQhj<'
    'Pwrrd=O*V?ecp;Sqf}pcgCWCSxPKsbsrw~z!)fk8j%xicbXxFG2fn^W-hOaX-k;UV{quOq<FHEk`0bw3*ScLJCMLWmcB#WJ&mhmN'
    'T;sgH#5f@fKZmKwMd!G*S3dq@rt*A%_F2Xk5zFZe=5z=;&wIiO@2AX;tsGx&^(^G8TE3nuP#!`#gr}&?8(ig+S2ix!ijceeH~Km4'
    'cqn{Y`*b@)hIz4vOPsIzI2~{qYR!^sdF|gCPxmUY?)g>^;M?926YG2{8}^JmOBFrwmW=gYQ!DSjH!pHK>}Pz5cbqeL-C3QN*YJIW'
    'U8F$P&d3>a<kp|Hm@J_d&pZeG$~5W=?tSE}#aTRZGwlf7P|Sp{VlRjbA;pHJ`Yz_0H||2za6*`EufO%NZ{&v@FZ^yv+fOT<oRC9V'
    '`>>Ri-xGMboWa-l=E{!sxH_P_0TH9v>L|!5=zKrvLf=Q&Qw81$&lKxax-*d?ZvhXONt0{ZGL?PKa^JOj>dP^5vtQ`^zE9lj#r7Nb'
    'S*~(Q&#)xw5x4G8i1Y7GQJ<VQWsS3<^Dm!z3YR_bJ14NU4c_To^57|he{X`pE7j^p9;2M$26<L_rj2+$%_AH2%Kitc!m6i#)qA+E'
    '>5d1?B>^YMJ6m~ttJir|N8PC}eDIm0Xmn>N7tgNFdQj8dtTU+YL%b~RLS3I_zZG>)y(h8YcbS}fy)R(T@ix@IDP*~iZ~Psl4E#0z'
    '<a5?=O?qARx^J+n0@-BIpHlDlqsucKCTgCG|5##f#D&O~6RI2PXMC-1Dt&-Q_d#auDt(H$Db~2PZ$o7tgK1+Q6o*@UwWm8m4ZRRY'
    'E!Cg&-290>FTdO;@Sw&`JhWr@oxa`uTC?hp^BiQ=>T#EKKJ-s#B8V3c7Vi=3;7jVsnvK40(R&tmRR&WQrqbTjt-V+mu@W(z?#L8<'
    'E8<~(kH;L)KIm=@^6p-7whg@8kT;2p$3?T}C}Vy7HV^#9J(vmekVk}czO;pn<0|iLokP?(>i2quw__{mjlt%nZ&B}BB3+k#jrN@('
    '=yy+?#LtqDi#PjCbcag#?<ncM2#z~dcaeB++#VPE75B>`%;}YRyb;MRomV4A_V`^Dtiv(I`$SadlFgRIImO?+kCJ*D*cEXb`CMlR'
    '4pyc1-5Bb*&~MDC`21cZ^(KW~d(bbx;{_bwy2tj%|Nb9;R$zw'
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
        print('City Information filter update already present. No files changed.')
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
    backup = backup_parent / ('EK_code_backup_city_info_filters_' + datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
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
    print('This removes both category-button rows from the City Information page only.')
    print('No database, media, migrations, routes, views or JS files are changed.')
    print('Stop the Django server first. A backup of replaced files will be created in your user folder.')
    answer = input('Type APPLY CITY FILTERS to continue, or press Enter to cancel: ').strip()
    if answer != 'APPLY CITY FILTERS':
        print('Cancelled. No files changed.')
        return
    try:
        apply(Path.cwd(), Path.home())
    except Exception as exc:
        print('STOPPED:', exc)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
