#!/usr/bin/env python3
"""Remove the City Information directory category buttons on a compatible PC.

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

FILES = {'templates/info/city_information.html': (('715f0d1f38d730a9c1ed3dd3c74fb89b7c60325bba7459ad6ffc52365fd64378',),
                                          '7abdfd1ee5b68f6a99b31ec65d90a55079e40fd1fc2ebd4471c3b1cda9aa3a76')}

PREREQUISITES = {}

PAYLOAD = json.loads(zlib.decompress(base64.b85decode(
    'c-pmES#zUGll?FEwIk*VFx_S%z6VRT5W2EjE8EKiizSc%DH?5PV*dM_tO5iG*`A4+2S>Mns>;edd2*@x&%X{I@jh}6AL-v=vfBOa'
    'g@^1v=zo7==Me6ae+v$A^w+=t^^q;twi$G6L*9DXOX#aX<QmJ9H_$^@jW(t@3_NjpbOy77+tb!Vv-1y)aaAR-d)>ev%reUucN{}G'
    'no@V?O0$!fb+5kK$FukHdn>-2EHPdCYSeMnC7uhfjyaRHx9DicO6D4UHi!29kEFfnPo8=?d9gmSjA7u$hrm_)M<y%eEaqy?ZN<v='
    'LsvHV_KLkkD|5W})#brf`<at<H?-c!p!J>)p4w0Bc{g%0Ve6RVjVsxamuwID{;^JaaAHO9VmbPl3mr$*54M>`nyMddb(p&1_>b1p'
    'm0m*6^528;AII#jptqw#>n|>WrjAp~9A78%;nnU5S4WJ_TG-uTZ}DWVZLsgX8wwj&l*tAiZ6hz(H-p&;V^3}}i`-=TJQCl2e7XOG'
    'bTwO9qH^>hr{5zTkbKe65-)-cy=%#AXB$E^5|q%3`$xMc?|fBAwXpd1ll`go3HFV=s2Gbe%m1CNVDl4X%uHz(*y3gH#taj+IkY#}'
    'Z?H|ZH#xGUA>nFbiQ~OZdsF-AmumpmkaJ~8<Ett5V_J{)G*M~2bPbtPvWq{6QrjFuFM8)@o8hnFyn<tK3`{9kU?>_Hv%rhfBh5P`'
    'JI}Q*Z3CIFj^V>c#<B+;x^sq))G=h>W*E7zoe<Aum%dZ=$cL{vcy4bxA<ct#0eokp_56(|y`QkRGkh?!=Q90H*uEr7dEdNb<IUUU'
    '{na`+#wGR5G3kK$mX~!dz!&W+0#4xH%7)=|x~t=;il6E3nPare{p#8YZTcPCr;*u(?Uo_%wS~S87JO@Dl$Z@C>)l#=y+E)1t!-+U'
    '_Yy!>MT_+S`;OgA*xBarq-~!5(RwfJ+xLas$_ta8f_LS2=gD@q_r&qZk73idLtp`qj@VBv<7o{%29~H_HI*>hJ!AhH(w$|TAw$&p'
    'n0FK3h#=GZ+QIkmy+|8$F?Jk{Hs_P~TCNkj((q96;m9iZL)3wR@eX(aFU)qXIK{qvX19V5a}0q)&cF{F_mi!!D@=c0ERao4Zs-wS'
    'Lg3&8Zd9~n99iaY<Mgy2y%2JcECc4pF*qgyMz9}!Yl_f8O#fH1kNHb5nZJY<Y|ean0gNYI!S8iDA7(d#EIY@TZEfQT_L2i|9OSKz'
    '*VcaAPknlx9DY4sr>j))?id!sI+GE96L1Y;M+f{Rd-c7n-MD|S7r=STTI`#?a`6qlSfj8bbbBHEC|Xp^#krh#t%{MST`z_`V3#Nu'
    '85qm`djb4qmbfl#-_ZRRI+oZzXphgp?AbS`Yw*RH_Td2c#6?*1Xn|9)7SlC;i?D-0-+V~m8BtGdV8S+LD>n8^9S#M=RmfJ_?&=%E'
    'gJZ&{3LU(jPgbILV3Q;BGaA=Z7+$&GoloGA0P<z{jk&vo#l0PN!7qwrioO6mL>~8l!ur+DaodJ>ThfVluTA|zPg^V50!xgm%kM@;'
    'fUz^^+ADYfan@?%fO6g1m<{{>$7Jx*HYWNobi^P<0-wFk^_i```TBf0>o2d&f1jOK@TW2TT&^v9w=Ui>j@djtd#~~WydT@4aE9Jf'
    'hsA~|@T+u)GZ3RrgoC-*hrh{xVC%pQpPon3%MZ-K<<9>lY)#;Aej9%p;~nyaYYS#M2ddmg+?SyH8&3vpHnPNE?-dwU<r91#y1hge'
    ';*H%`I5rU{z>CC(;w_)S_w+pZ*4WH3-VT<eXW)dRPjQRoQo|yy0Amyr%N*x#%%72sflYa0<hYY=zE<~r8fyox`SQzK2){lul7sv='
    'Sb3(794&hG%_00rM$SaK5tN1>!LI$(1)d?-al-gzcA|X2q<BF&7RJCn{5|;ID&h*$9k?Ov^0*9s$#u_jI_bUPr*Cc8+<+I(BooQQ'
    'b3r+P9``=WaXLIcn0C~Z`_nPzaBt0p4fdW<o(Q|2EyItv%_=rj1H88sZA17QlKoD|Yn1}yLvXP7df>cbLN`1YI+na-{y*9!xvd9Z'
    'fFGRKEAXl(bpsc93Fc&aAI0CX6YZI7Rq)sOg!m%nTyt*o4;T5JH81$S<U`~tvy9aZ63cm%$-E1!&H}ezKI3cj_&CVfcu#!Zt#JkM'
    'KDfC9ZlHWzz#7kpXUGNm_+}sd4u^c*`Gx)K7>rwK9&os}ZpIBByJQw;Rw{fl?hEc<`cvE1a-WcNHp=4x*FSiDUXy=8{0}`R+JNi<'
    '`3FO}>KmG>#Oz&*-ylyCkS8Md3L?8r7lX^$9q6bDFZ+*p`BRJe{3E{39{kxNV<QH>jS-vmg!qDLAX=MhN|GD=le)dSuE`(3pNM4)'
    'AB=~4G=Is3eg@gjq{rL0H=QsUkVh2XF~9#}46OtEY<LdQ#_joB594LY7l}u8W{>$){(qVCE$O@9{CrLLx!4|`DJH!fSj?~Hjrq7+'
    'JpAsua`ic|1-uf@7sxAK@8_@ha4`n8w|?-X3voi?t84OghU;9`Bh^x_IevD@m!;Wmg&Z6lg4!?oX)ksm(|fW_Z~E65UyP(NxbLYZ'
    'Lp9#s_!<29z&6lDSmaH`-wg*GvsE07;s|~yTv<(A-#d%PUNYMw7DVlFxu3Pzq+FA*pYIiQS0K2?5Plw|CSt5x<DU8-a_xf+zwqLB'
    'o=4|$k5J?Lh7f`e_wY+rf2^p!fbUSeW;Q6-<NX-^9`zs3jewI&@R4lqbX4bG9&_6EHBr~sNnIx3;S%MXzI(scaDBtkE5lIEjWY87'
    '@dma(=YGcUSJr2>zXqSr<umxA;|dDK>%hje7P}kvYmFC{g!&u$$$jDByd0A+5AEBQ<5zH7Vy6|47|Sr((DNPM5&ud)+I$ix`Lom$'
    'mp6I7%KZ)G!GjtWh);eL*ez;dQ|b$-=ixVyx3z{6e!E%sV3{+@k&brOUdPqq)>1w-VovKAZ4gC%1DAO|f6LbfbsPQ9<!{*U?M}8F'
    'BgGyO(+9I1@~Sd#Lw>n;2grZJr?t*Frhi2I+);m|>?zRuxU;4_fN){q9rYz)n@U_P=lQ4M1Ca~a@BOm7gghB!!5T}{GS951WXIMa'
    '@AXpOX<O7B9>w({=8|rEE$bAyekCT>{NQoT$8uX&l&|&pcB@hAx#gDW;=Yc)=f(#)dFZQ8>l^<MJ8mdoo_^Zs_kFupgW54A8B04P'
    '@2p4L#MgcP^?xX*#CulWbzkqpi{pUBVCakWCl?B<mErRW>kn<@{s&?$a1?3%e2(lT)~;*e_hS2tIH|@(kN6&(L-|Oh|4{PCq|Co6'
    '<MO^lou}@wbl<CxN*TY`tEkkQU-c`BUg2H8;<Nn097i0#PdwjZT&6W~|DE2&`=T@ME_&VR;;sKW)8Fsn2;yj#_gDG(g<0rAV0~4V'
    '$Mc?U?l)!4UakMulSOB(#gseK8ICZ;o;F4Qv)0E*s_}v4hLw4u)vaz5>UL|%3yE*1335GY95s0IT&!>7y^DIw0l#`;{{Vif$?Zee'
    '_@4UDEtq|3@J$_$WnS8v16F&QLSDxqrcvF+F|p!(4Vmg}jOhbU+L70C(=wO+`rEs@kMDhcDRdCl>fD<zRpa}!*ZXo06h|Upf!lVT'
    '=i!5Qro&3?*z+EiyhV&V(ODPk%bM>g{id@BPtsE#;}BcrycZNw40A;RGV2|C{<NMV#-aYYGW@B*$%^4?1H=>H#bv#BHV(N%A3pk)'
    '>k07|YongK`bLD>c$i|YiVaJ@=ep4q*5eq(O6br&`wG>3oeBqiRuAnd9+&-kzJC6^+4E&RpWH4CYqj-joJZde#(@hzr1vZr%*wF='
    ';$}=7i<*4n2#6g9;i4WREprI&Lj0Jw_5{IK({<&Hg`Z3C=ixmsQ?DlfCg$fMrWhRxx$_!fi+m)g%*D@5R60|7JCNT&KM{B>v#xo4'
    'KwO~?p|iuvF$6m2$!mmsOs>zoe#ray`TUh!AN+f(PaeoQN~q4^J%8wqdRxRhxlZK{crVR+=KS25_!e^F{m+lN))sSb7@EucY&Xhn'
    'q4Ro(_w$9MxgYqfNV%A;_B+;GxLO8beu+AExXI;eu`ib`ACs>uaJh>!06u@c-WuHWUA*V(4|ARCE9$A`dJNpb^fNuDuE^s7<b*%$'
    '<(Ay4%nk2jTY9+JJU!$#r#?LP=r#Aobs849%KZWQy49jK>i7%d%J@%-M=oa_izeU0XEy(i?sMD>UE*2^xsb_wr>MP=Klv<{lsNBo'
    '!IjfBofT5f<Wqh%;CB~py{~WUxFyEab(zP^a1s@3Fm9A>)Q*;EBQK!b1Z%Ln4^iq4^ebxSfc5CX5!g#)i|p*Jz~lP-$6GIAr9<@t'
    '>*o*jfcj#LkLV19^<%)TBILiF`8M<Q&vNvet;@R!jk^0m-F)+<Qun;~d-MOYjv2*t7O8{B_1H2IcV2hlv|=-t@A2x1QR1TB)*kf$'
    '=<N6^w_}LqChv{<yb){WGI(W{+1Ly759BU2zcglB#M&$PJzxJ5o#s5`qkeFDu(>!4slPiZFdwscNpbkd^6~bb(x<wGokNTF#L7DS'
    '_KfQ0a*dyr7{_G!;4!Y0i`J*Tvhm6G$nt^eSpdf?oh<_Y%6SwMR#-nJZRYsRp2b})U(FRH<RL7F@Q<kJ?()ey8y9O0{5|y(@9Obp'
    'JWRO1p&mj#06*w;D{;Q;<6M#ZWmdtptoCn?zwGh;SnHX5zjric>quY8#?H*hHdPF_^qLxZxA|aR2{G0jZYuGPaR$|$<-L*$zCG9l'
    'dF09y>HBfSdykx3eYKw<77@R$z*B)6r(tnt1^#*R$R;M8?<?2~-J?Pd8EQY4`CP1?Ozv^QdM}Oj>CPGO!|^hI?H#f^KP_~UB8Q6H'
    'q>#0^Z<U{a)#7B+j<vYjK|Yp%ixn+WD5p3&nO58lIuhO?55>A8)gE@t&ONidC-_jNJf|=AU9G1+9aHZY3g7pM_Fn9>HE+GQljni6'
    '2)5n3jk`unH$A_oPkt6P4mi3)ed%F!5BdEk9lYb;^5CtF7>~Gi)$()L;@r5nGeLJHyhKO6@+%DXUfI*X>pis8bR)5!(S07o!A2h6'
    '=yl%JQIG12An*jbj}}m#$euONdgyGiosato;$?A{q&TPL=OyruWnTBxdJ+S=H>E%7eVu_X(J|mV0+;0zd?Q}jd+^uQl)CkNk?Hki'
    'y@Xx;I06^E*X|Iu^rMS2oGH)MZvMmPULM^<KUjqQ+8JT}o0~qA46$8s^+KO{+~j#l+rE!<U$3?gmZ#SF3OT?N>cEO#_+6R>J@36@'
    '&)TQ^1Rjo79S?Ug{6XLDajjYO$2TkoY4*4aKZ0EAE512TBGw}gD7T@WY`w3`d(Zhjrw(d?!zk?PZp_zp40}&!p5+}k;$eP2PryEi'
    'r@F3sru%Ydtkr%`B$>e<YduHQag;x{@&MzE->hF2t=Jf8Nc*Gy7rS=|E;Nuw@Uz)hc21w?oy~KI8%KSwSNPx@pYGwn=7n!j@7gC_'
    'OL<>It>5b*{X##*SrYX!s{JOq+nW3D(|VS39PkSJK+pL-=zPEY9_E1NEc5upr(U%|IWomGI<sP!qC1dls&mO^lnc{de`nN3kz>cC'
    'dxa7BLjjld=?+1o&)fxH({I=zj_BSg^(MJp*E{G}fc>6+^pci4yX$}b>#zU%Z_Y@i)&'
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
        print('City Information button update already present. No files changed.')
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
    backup = backup_parent / ('EK_code_backup_city_info_buttons_' + datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
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
    print('This removes the category buttons from the City Information page only.')
    print('No database, media, migrations, routes, views or JS files are changed.')
    print('Stop the Django server first. A backup of replaced files will be created in your user folder.')
    answer = input('Type APPLY CITY BUTTONS to continue, or press Enter to cancel: ').strip()
    if answer != 'APPLY CITY BUTTONS':
        print('Cancelled. No files changed.')
        return
    try:
        apply(Path.cwd(), Path.home())
    except Exception as exc:
        print('STOPPED:', exc)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
