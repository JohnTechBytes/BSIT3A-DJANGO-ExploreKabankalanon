#!/usr/bin/env python3
"""Install the sourced City Information profile without changing the database."""
import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import tempfile
from datetime import datetime
import zlib

FILES = {'templates/info/city_information.html': (('4b280087cd9b9da62b5bcbf169bae6d7f58d94ab36027be8bc78e30845522b25',
                                           'bcde7c8decbaaad9dabfe7bf0ca98ab882ae6fe25a60f714472673cf6ad7fe5c'),
                                          'b791b428776ab18f268febb035a52f377fd870b17151fb84a78fa4fff1bf7a17')}

PREREQUISITES = {'apps/info/views.py': '745d8f2b24e7b2260ceceae3f236a130fa4d7b7c6af972224dad5e3839e80d37'}

PAYLOAD = json.loads(zlib.decompress(base64.b85decode(
    'c-pmF*^{DPll@=5*N&J^P^ycGm<LfoY@y1H?PWrs8bm;+T@WVbf1i^VP_V4te-9nivfL$a=E-yNUjFxA$G2o3ua9qse{a&SyMKF|'
    'WB%Xtzi-L<xY?!u5gwEHU;p{9w|o^iR@iY&Ve94njjx2UYp%}T*x0yA99jG%^!U|jJ)R%kff`J#&KG*eRm9L4NQJM+owcc5uiMGx'
    'Z1ab}SK^MVtZ<zhuC2MCj^dM(h`DRh^WsU>zI4@*(esqc*-MP6ZB9ZrIfkwxpV*i%p1Q63w(UgRz8PYKXA6uu{%YxaUs)X;Mb6i`'
    '6j6Uullpr;dWxJn3n^ab+;(m0k=u1*FWnxid7_`gah-^qmk9COg6pgm<LFq2SXGRZqf8DiuYXeqhB!#+TJ?LZe_LD9SJ>yYrv8_g'
    'P*wDUZRy49Vp2E*u2}PNrf#Gi=9auJ)Clw5yBjWYd4X)*Q6pi=o*B>2c=zn4^Vm&i&r^Q%>4)=A$yW2PHZPuhjME>G4QPDv$>uMd'
    '1G}r~eCL>4JmtiVm&hk)AnbgFJE)ub+3(Cxan5dc9(!^9F5X%F-dbVJ&lqEFb?2eOU-oXoe4^EcI>P#mw+D43#7=i|_Hyaf=JmZp'
    'b5rEQ5Bq@sVw_*?u3lKYoKSx>r&opgI|LZ>f!4(z#|OvKVHcxwTbs$}$)e%Mybhld3;0kxHRqw198T2kgw}bX{%~zD=3;I7C#$Oq'
    '9&G3?n13ABrU1X0#O|=O!F9o<=M*FM5mReiccRXQ+QGdLu@k8SKk~ZT8FR}JYq_%!=y%HI)wM+}>gReix@bfDxHc~b-_pqjEVjJ7'
    'bAf-+ykhtX;#iEBpU(Dlt@<rxw&}+hXXnkl#4L_xyXSIjt51VXzl<~V`#zrfCyE=Jk2{E&%uB=sV~Ex9A%LIf4j-Rhq80CrgFqW#'
    'oMWl?!up$UVTW{T&ClL&m%o(PH*R;bbu1MzDP}K`oV@{8T=)w7F4Bh@r!9>H&xyY?CVIvnPtMiYdQ;2aJLCE8CGt3%4?e5o&KGrn'
    'G4N<FVSWgE3W=L@%s%QsAnYjnv!vYRoxMv~)16>^(q~nf@4c>s*xx>}YeV<|yT>8UIjo)BaTXN!7tS?>;w7ELo??XlAjqc*2mj>4'
    'w?U9ihjQX=wtLJowXOb>wsf+$Vbh*!huIU?uucJD_3Vtdr)s`v$2ntsh_O{LO^k0-vz&{ExjPB`ej&le^AI*E$QH2K)&X8P#qL7u'
    'pbpgx?PETZ(B_XR?8mvu>`5&~xn`>Q%aY-44*$--vqm(}vls0mXDP)xzq<VHx&dQhFD?XD2XAQCw<d+#Ri8XX+!I!M5!og_P0cVy'
    'yzTtquFz8EPq#5dQf%|99M=-U-6`_KTe5;}LuOlG6R?x(I%b@%$FnCr>SuppyiaHs<JFFS5(5h+uzmLH?J1)N?U28ToX>C#^XOvT'
    '#>gE?yj2I9U?;1dUD(ZMj_}vS<BiTsq_a8yx$pF8J&v|DN!Ml%ww%Bh`k6ZHqu;Vm;M(5dL-aX1>Cx)9V{8q3I=sRB6~0;^|AcSL'
    'J$y6XQk>9VU`gy+6n})*u*KLox~cXAY|k8UjW0v>Kz>58|7F-eXr_~YS!^*@KLiF{^wMW;^NB(>pWpTa#o0SuBQMtq{*d^4H`--Q'
    '{DWQizYuGGI=;PYdbF0riwLKLm!!=9XuG>M=bbg|qYe8pe(&lS(ITzF330Pdj0o|QtgYEo$wk0%A{x6Kt$9CpyWkkZU8E^0+8GId'
    'G-h58z43hS^1Y`2RXJl+jfrAG%wINo^rFlzi2cuu%cQfT$H!0367%V@^`?9rH?ZR}jqJ9crcF-C{PTY>pWICh_-MtgKJaDx=i-~;'
    'T8&lq(uf^J-(YMV;xphLz%DU|U(=kQd~goOny_(SpRtI;VN8VM3l6dB6b{y+n&a=~OG`fkYopSCf7y0@*EHbcqg^}K+C2?9<_l}{'
    'SFwjH<NQzY<9j(dLhgm%eqF$3QFgv^p!5Mx4q6=Q#^>o?bUD)6H?+W=FM#WrGf_p(C*QsCca`z2S7;JoMC@&(Qri@rjYGPDYy^9I'
    '$@Atl0DceX+2HcJWwr<wWQ*?PSosPx1n$+(jr*VGz)tkVgJT7it|RWbRY%7Vv3gqb^1(KH0p2GL8G(PE-Hil(J_EOQNSDBV2J!J?'
    'O7<D{zEIoh@WT3iIA7iX_USwDZ0M=^&gE&|KI6N#sWYBhac^j^47{7Y_r(0d5ZRnP*r^<gM?8B2{*3ruiE66Hi2rC^*{vE2c!9+E'
    '1F7?7Niox5;7;Ip8&wfPXg$0)LK{wq96|R#BmSyq!mplXkS+|qvVM?HOg&yJ;(_7|&n~OB+V)d?ZcXd;=}UjV!Mv==-d=Ecx8(V&'
    '+6H5ZgFe`Md>Df>GC#e(n>Xe#W*RO*PLH7vunxu+x=HYuj_y3e=QH1$1<)~>v+Qiv$or&`VB?bwJi<8H-0_>YP3S;8^VS8|<Bfv@'
    'n>*(GD|;7y-qbQ{(`Gt`je+^rg!7?G;R9D&`sU;aoZr00mF<Vw*-niP@b`4}wSma|f&IpP*eGQ73wG4@GsaQ-)&u{(+M{hp<pNxs'
    '2pB_!VfAwyFj!{!RE?NFK7%9hANXR`Z|fcQ{A+Z{9=+pOaSWY(_OU**PP{S~(%4wVqq(6yPrLn3h`$_bwf+9Mgkfu~3)p0+exjIM'
    'kseO$W80qu(#nOZ$k0U4sO|VX!M@om;;$Tc^_SWD@f?7~9eYvxmqf9)cQ(+3={#rklP;?rh_4H&1HB)*^7UHGc;cXZ4{>sLpZrJ4'
    ';1h>6)6=tn{0zR(f!|SGf<qtA;A@C&8PDwFm(8T?cX45V*Cyt<VeP<Y)ZpGv%lsfPzy7MsV<(Y07yLurwrqk}<-}>_f2BWP3TM$8'
    '{}OTBW$Q6MekMGJ9uzDdd5&-!?}N)E>>hlc>J6=X?bv;9i}57`p5&M}(-vw{wm&WV**li@V2rJpWBxRt`*r*)j5}py2g)tTf3-fp'
    'wE=!uKSy<+AHDMv@mID5+{e4&)V#pX#sN6AwbL!I+X$<i%lN7{;K&x$|Ai8F$X-$JiX-2PNviYsR{zK_qKV_xdx(=NSN?3jLi2iw'
    '9ptCWGUo2vhh`7m_B-Hv#?k9u;DbWyD*@#K=9kr2Piv+%^k<hiL3h6UiaY_X6e50!A8nZ3)9vAAf0f$6`s&~*z1A2I%i!I1`<gP}'
    '`yZ?gY;n!~^}m}Rls?z=gJ}{I*C`k;Y0sVT0y=fRw|U~B@7KoW<@~{#T>B*7t>y~;5`sfb5U26MB7WS$j`qJ-B|bXHxn80n7vExW'
    'n$CB=$!**O^OZ%$2Us3PEc(MThu!)s>&oT*%NcwLHuB&n(1z*uosDjJm3SOt>ybT5K2^N7#{_@4FyF#j?X;rh*Ec^JG9Rk2jX1g<'
    'VePXj&Y1sQ`BLlO9Ud=)3^>(sIT7!JLnF^ObMoE#J;ZyvJ3+3DJ5?-v*ly{Q{SVjo5hrN)?bUZ4`XlKS^2s|pzw>wSgDW1@m~mYv'
    'aKBCEN9DDH$FFYV83N-g4*3vU!12M0o4!DJ@~QUSnwwf(nS-W6++e&9IT!chGOam})}*oWn!C04GFo|OC7d7gy}SL7aUA=1e#!i-'
    'fuF<^nl}9P@!zfA=-t>VAF1a^S_#^A!Rl=}(>2iE?wB-5FEAL!$S35#9n%t5evA7_C!jn|eqrMt?XO^Mz~7A&oKR@A^W`oEVi#k7'
    'AD7Y!<DohQ`d9^S^2}=E?>SS=yO5WGEtKn-Z3hqfN#=;Rc1~=?!SF&pN^=OkuGY*wq1`2IB^2%ac8%e8I)ZHRo_D{;##d$ZsK1S`'
    '^nx4yPdebPXh%NW?OXh`c7j$s&={}lkZNqN>E6HI^QXT!&TgrzykZ|hU*xq8w5Ya2IT-e0`z%Y^cM`jZc@ezo06df5kZa*bu_{+>'
    '<o!e~0`6tG{Y;qD!lIAxe%Rp5B_>^Q<n_wG8t+v)rioM3Rvm|KB6cY5m>!bFi*FhfOH4P{_dbZp54hNaI?=~`>`|@cUK4$oD_Z(y'
    'HF-6RSzwGpSsm#UL*6#yqRGX6(5E2TSV!oC*8W}#*Y3vixNbxI=@~vdLJWmxFNHnXzO4g3?FBaN%fW|%UkU7VRAqlpd#Q*s=*BGY'
    'VZ-%+)v3N!xPW+wQ~VBHs-=Rb*sLz(1IOS~ip&##v00717c9HL3fP_WfJb|AY>$?3ZGwEmp{><Pl^IT^z6lM!sN+At*kDuORgI0{'
    '|Bq`1c~<!dVX1!GKVZDEchdw9dEujdu6G;}+#C82^YV%w_^xrJy`;Bgtx2gKG~uDcx`gSlWy)-v2uH$wiVbiws<R5M*uwg~wl!F='
    '#vJVh)xx+87|H5I<@lsM?D*m^ZJ`BAUXN(*$T?Vt3_jH>^Tci6cj5tKD1KInk(T+Lv>CJY3^^EDQp%|Q2piEer3N*%V1_uR{5IY6'
    'ds?)`oDAC2ZP-2Tc-Q=`?=Y_pa#+2N)%7sMGa=RO-%K%|4kXwIYg7HM>{Pcw8WHo!%DQu^lRgb-zXk8?Z8L)p5SJyaDmAVRzw;8N'
    'pQ%<04i$&)SSxk?y^SL}QxGBt+lafc<Bz4{W%GQ74|F{x+`9we<XE#a+b<p)n2Sbx^BG~Pmy5Z*90@N=?@asRFGE$(x#tV8vO7gv'
    'u9<CKW5R-2ou^qH5&4U_UF=2K*<SYUawB2q)t?%*qIt~f{$uUa>unG0)2vxbOyM8kh3JRyaC6<KE~wU8`(;}<f>&E>^SJjER!>H('
    '$VZB$r75RVQ!WtG3gre`FY=ce)fr4ZbdgJNZ-JO%xM7>z8Tx?Et3<RWc6(eWbp*Z)o#FA%fosxvgL1qp<W%3hoJp_1w_A7yzc8F}'
    '9K!#><Mi-d9hK%fzWG&eH*he{;aZV%b~a%I4wb|de+9+YbVK(Hswdz4VnFi}n2*t317fC7882>evl#2Y_c3?yI^d^|oXWLpv{!rf'
    'o-vO)C-0DdGq2d4r@V2RrcL}5;4|JC82W9!5ZmW8B4I&TU(KzdA#Yg1a`9dN#Qp32!=Jz>b#3XLk~7}o4ZQB`41eBVs8$U<v`5aY'
    'IW4Otq0NHDYa+zpbd*CVKXlg0s`8P`;jMZW_cmC|l-3n(z~-xJZ6|S6<0`JU04J)}dFf%?R2PGvNbsqg`DIm4_j&RG=wPfxJx{Fv'
    '#2;$`@C}$H5{GE$o46?V5sx$;!YATC-^zMcwO3<l2l_va#qAPa$<cLu3a}M%?xaReu@3*Cwb~<hN7a78shvNiE$yY&Sjp^O+DP(E'
    'pYyu2K-*-2w%iJOad?a$8)@&c7%a7hjdyLlw@jW->M+QGOTUD9j@dggf3zghx8aobMsup^9rx2tEB2zr)rRUP<Oe#V#@6<cZU2I='
    'jvZ4>fhXB|Oq}V4e=Y3`9k<|R@}+O^FY*Pl59LPUB6Q{~Z{*4Q^`IIn<t~->v(T?lVbBErn&PjH7zO{9>v$R1Rvh|-O^SR(K2EFL'
    'cVc_E%7nNOX<6p8HGWd=fG>8~?@f7+<=&w!=y|WuVK-<Sro}L}19E*#Sa#(qck?B^P@ijBkAb;k?P;2e;8jAm5vS0SlXTjp`EJi`'
    '8|h8kUh@^>SJn)igM8bM8Rl8i?rr%Oau%IWgFbhbzlk%Lvr+D^OcpDOhpN3BCxuN}?HhVs0@sSqR}MR({a)jUc5=oyN8lWlmVgg*'
    ';gcPvxfQ|_5xLX>-gkmU3ca#m@%cjh%{3>bR;O6!SG1Qx=lbw0;kHD&i#T2Zzk%&p+q7qczU9In9w>%mcE<3=Rl0PJf_xP1#8kte'
    '{;)1Qv?A5s{;^oTuE$+0-|Q;2weH{GEeUu$uoW>>e3t{q?>VU|>m9;W%E>nP?#!at7W0xXUg&zE4mGl4$j(*rvQXhbJI}Hlh1eVI'
    '!6~<aR*VjGK1+)#-C=FPorTC98>BrD@AR%8zJVWUZ(sV`VteD(W9bYG4#6p|d%DOCN7pi_p1o)Kqzmp*=9X864ZM7Yf2@!L!6z@*'
    '_Y4KGxcH@b&pdvF_C$V~O1mjv>b|u}9H-=f(=PCs*D%JL-KWK<rwwPEwp?Y}u+R1!$>(V8SF$cO?N{2hJU4sihq!iI<7SQLito|o'
    'w!X1MXPysLPOSJUv`URZ(1AbTt1C7>;^s=6dF)Jvv}ET>Ey_1~0p7=9O$dKU8`ZcT(i%1Uc6mF{qER*-27*>;hx`0Nd$ZIZI|mAm'
    '1U^{!md5;p^jNLQs_Q|?2WAJh$H;K#vS&I~5uu?jRjo*Zc0rDZzWtS$_P~LsiGTJtLbe`M=d$^jbWqhU`GFrz`KI4Pj|}@AeL3Q='
    '#u=T5CVs_yR+g5tt0rSPZFBYUMLkBN_zU@4BcJo3DG&$W&EG}?vuNL!_&516#m|B;z{J>0;TkJ5-q@hslbf@+I@;!*xch<WlL2wK'
    'YrmDRz1JX!x721DBn#$vo@v=Z#Uq(+K2qK606hfEAl>Y9bROm(<NuvoA9QY^!sM{3`5aod{L^^c8g#bi>{{RFRR-gqj8jLnFLcF4'
    '>&B-U{~kzLSwkY9qS`=wtaxsjf5*Ry=gcqb{hkf=SK=)@qrzesewI=#ywZa?o$X<Jbnms{mYuUfEVA_<^swHfQN$zFHo(<W@O&C8'
    'V$UIdP5C~f8V2UZVQq4%dE<9cYbK^c!N;*)|DZoy*QkZjPBr$nj$z~4lg_!;MT$Sq*Txv*Np;3u+t>~KO@TMvdG2EjWWVp{^R@<R'
    't}Fb5{G8@`s^^2Xz`Z%Rk#V}y{|9wM=Q>5i`m7wwXpZs9hz)}{3s1bUj^EpRpEtoozj667@!WY_Ys2!p0OMHd{_1?lxLLcB_g*TM'
    'H4ku2hAWGHt_?>W(yPGv+#gU)>bc_1I_ISmR;#OONYJu6^rLYgyk+fDO@cSJRL6#<rL%}J_y~Qkf%SFvwC6*0dpffMzEE+(EMWS!'
    '#x;63rF>8Pn7)ya55#G}a~ba>&P?Ydyum-FBUY4iye`>hUge`UpY$L2(5>eG=RUej=v)jtzYYIFj4P{O!ZgBt<^zgx_GnL<<ySFU'
    '69=XmUa2kaIAp00>hHL2>##bo?@*MO)mO1@UE(9Go>0bUQTs}brR?5FJ~&noEEPFI-*r5HK}>|`dr9Xle1-Ta!-2L&qW$2~R}-K1'
    'b4t#3i&G^=Ow2h}GlgGJP2Od7(|^n-Ug!)DcyVk|t-mWBn8x6ZxULn|_erOf_e;L^vz+6)-~CH9eB`7mw>I))&B^Z0iZsqrG`N^='
    '5yz0X6^0+*VR)^(c*HQ(MpJO_T#W3E_~Kap*Or}PacHx%&Xl{d(>j$>+K+O_Gf~|-z&M%o$Jwd4sGAtw`&#IXXWDT~=fKoWIX3bq'
    '<Q(wbz3}e55ON*bEzeIx!u@w*A>pP&@roP?u6_2E=fF<4@Jl+MK0i_09&s!Mem;E6SDF4{7+(5Ib!NHcFLT=4TJC?&CQ(@vsM^7t'
    'tM<$M_VGAKcUx4yr98?}t){5-Fx9ew%@hOT=56uZnMVCHohO{-(!gBw={Mt8FOBp2S1eE%A7f`hSPb#4^Yd*StGGprE5E;1p071M'
    '<cdku;tO3PE58N($d+|Z6>oFoS7&EAIybep#fyp6*8j1#)xRzigU)9aRtG-Hm%N+o?kPgU7lEULa__&ai?SHrG<7lYu{H*%<u|PC'
    '8>kL2Qhs_{sCO~ew%cvITly|5gANtolRMiq4sH?fQ`qh?r@F>kS^J>c^1Ipx+xvX_flUrpr`jvy#MU>G(AOsixM4KfXL-8pm-)(f'
    '#+S1i4>)KeHW+45?jQ|G`%8$kBlP@PAM~;*I~NO19B+@S&M2U3B{nv`)iH@X_<Pd4RI?*L@XP%!!nDY?q}$&6RU=g2r_}oTe$Rf~'
    'Z=OSVv>#pV@2<c}=keQ^_)V$z=p3q3>8E#l$irW&S54{6g<|xmuHg+u*lrHIXn)r_N#vt9Ji><ay)*1ww8HD?QNU@DUDTLS=BhEc'
    'UtGLDkI(r1!6|E-4Cj6=_j%_v`)(vayoA|nw>;DKx@z^4P@U(6ulB?u?z%709wVLq5ZRelI`@tHrT*T4@3B7AkH$vl&WLyMOczvf'
    'z{ba4h!>u~wSWl|VQT5&w3wZ=0qy<kL-1&4YUq+W#I+%_0r87^pZv)&XV?80Y7hV4za<8J8+Q9%O<{FZa9OH5tZ2Wl%CXYUhQBkc'
    'FymYWcF<Xj@{HWPI)m*rwG(l+xI70`V(6o@yx!o^`As_4P5xNzhg7vMRhgfOC$n<^3UoE$RXUH$y5^j|6Fsr`9z58yX>jm0ebYkR'
    'm1%=32fcCZF`nZ~j#tkIYsbD-c`d(Zx%*Cd_h0||zyAjrsN<O'
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
        print('City profile already present. No files changed.')
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
    backup = backup_parent / ('EK_code_backup_city_profile_' + datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
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
    print('This adds the sourced city profile and removes the duplicate in-page navigation if present.')
    print('It changes one template only; no database, media, migrations, routes or JS files are changed.')
    print('Stop the Django server first. A backup of replaced files will be created in your user folder.')
    answer = input('Type APPLY CITY PROFILE to continue, or press Enter to cancel: ').strip()
    if answer != 'APPLY CITY PROFILE':
        print('Cancelled. No files changed.')
        return
    try:
        apply(Path.cwd(), Path.home())
    except Exception as exc:
        print('STOPPED:', exc)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
