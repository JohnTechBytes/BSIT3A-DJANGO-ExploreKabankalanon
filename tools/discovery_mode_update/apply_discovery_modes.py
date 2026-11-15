#!/usr/bin/env python3
"""Install reviewed discovery-mode changes on a compatible local project.

Only one backend view and one nearby template change. No database, media,
migrations or JS files are modified. Unreviewed local code stops installation.
"""
import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import tempfile
from datetime import datetime
import zlib

FILES = {'apps/places/views.py': (('da810d083c7a1f9000d04ce651b4e59848574aa16b42d99741a306e07c82508c',),
                          '160fb3738111ea109ee0ed57e35cbaffcdee42fd518c733639f99e91938f0865'),
 'templates/places/nearby_places.html': (('02f126d840dd0264bacba97726b93edeadcf756669c0f4471315626ea8c0707d',),
                                         'e618f0a7357a2063260a1fc7d7ba23975f79d194e551b4750ce341a552ad0eca')}

PREREQUISITES = {'apps/places/nearby.py': '6d3f0d9d3dae228942cc902e8d602af3f2cf2d45caad7a160c489d43791c336c',
 'mysite/views.py': 'b9d050f5a5fcaa70c5eed55167ae778421ba07b000377469ac84863fcea6259d',
 'static/css/browse-guide.css': '5b4c4cf9bcf83058df614d7b45e48b89e1c3b8cd916c52f4ac2864a93696d491',
 'static/css/explore.css': '394b4eb54d2d12d333aa1377d494b9cea9b5314c5f9bbb9e7b01c8601d9fd64a',
 'static/css/homepage-pilot.css': 'bea520af0830407dea2676ae123a7efa15ab60bd24ba17c07ddac5b5b06b5b07',
 'static/css/map-guide.css': '2c657614f386c7cc474d64e1cb557fa08b435e67597808ae84f8d59f127f8ef9',
 'static/css/nearby.css': 'f6a2e32cad36a7a51530f569e9beaf4a1a3c8838eace0b7382d2303530d1a376',
 'static/css/public-experience.css': '4d7aef8ee25daef7570622c6106fb38bef495234aaa930d0ec6813d45392632c',
 'static/css/public-palette.css': '7f250fbcbc0504cf715f22c487d23fc785455c3112920e71ee1a3394f6e0476d',
 'static/css/public-system.css': '1ef32e84bc66d26731036244de1695e1a8ea7e20735f4a60aea8f04eb2cec8db',
 'static/js/ea-voice.js': '70b9e155cc4c3f61759f4967b019c285f37f46079f31c127c057880aa99ba050',
 'static/js/landing-carousel.js': '7c7abf02831bf64bd7175f729f7fe87e97a04c870ce8d740fdab2bdd04c9075c',
 'static/js/landing-map.js': '4f6820e19d0f6bcc7ec1fe3a11760cdf5958ca762f4c9507a2822a4bfaf2fa98',
 'static/js/landing-menu.js': '7910275111b8c2370bc19e7188d8cebcda1a1f42632c4baec3a5c6b13f2ffbbc',
 'static/js/map-guide.js': '608de1f7ed6f48b38cdc8a5edfb425237cb63de62b0cec8f1a23d871ff4d29a2',
 'static/js/map.js': 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
 'static/vendor/leaflet/leaflet.css': '337bfca5cabd03b39815b2700febe2b3b7edf55921c59cd49f88ecb328212303',
 'static/vendor/leaflet/leaflet.js': 'db49d009c841f5ca34a888c96511ae936fd9f5533e90d8b2c4d57596f4e5641a',
 'apps/places/search_intents.py': 'c7246a8202c048c3ea0f4e85fa9e8371a415c97b08451d10a376d2200ddce609',
 'apps/places/nearby_intent.py': '6017b22e5ebbe4b6f23acc7a16e7c43e8a8ca3a194f6bf1d6c5eff41493d668f',
 'apps/places/urls.py': '468713bfc2f4728a7613f4d5aac2fc8cc74e36719cf8654b61b72d6ed43201b9',
 'templates/places/_discovery_modes.html': '65cef8dc22b1dcac9715bbacd0c1e9d279f0dd2d3bff5f7bb1eef46b962a648a',
 'templates/places/attraction_carousel.html': '8dbcb6f94a77c6d83f217950f44894f43979d02d736a07bc5f8ae9713c71db74',
 'static/css/public-field-guide.css': 'e36f1cdc7c6baa1019fad7dad2b78af0bd4b1657a82a6c8913650761b685d08d',
 'templates/theme/public_base.html': ('48247a5822b03c367b1739b35620c670cfdd5a206a65faf8d43dd2f0e15d2dc7',
                                      '971b0e7fedd7b24d05f61f609d6ad03cb01eb283dcd6987b0d3d971bc0aa7853')}

PAYLOAD = json.loads(zlib.decompress(base64.b85decode(
    'c-rl~*ODU3(kA*Y`?kksBZ}@~?$9Kv3N3DqK~fC~iCB&1*m?KkpNGhZ%!I05V*me)&Bd}+4M}7O50{_2|G)p5?)Qg(@BOL!arpPy'
    '`?wtb=l=Gu|MjoJW^$XQ5{pS?znpF6=f<XWo^3m~>CiciM}x$)kXcWLt+Tr+CuZr|-KqFTx01ch3;Dw=HQ&$t>}@hCC#R#DKgsPk'
    '?k0P5DxE*Z!_0Pe%iO1Uw$e(@tIfr9n7q&!38zZWR{R@{n`jjB^nZHC$f>Kjj7Ry4d&{h*qt1RZYMy4pEY0C+zPm`@Wx~(X*nVS^'
    'JWncvgL}*GXQTYt-L@C)R5>vj&gt*<!6_}z<4sNfHtzX;<+>cF`Uj`nTFy6vb@1<+Ki~NN{36#`$lS+RQ)Tdz*0!9a2Id^Y-~F6y'
    'vbVxww{psz-K3kpPln~&IJH=~+rfd>xtLY_6n(y*dHJPV&EFf_{9!z7`Ls6q?2^XH&{{GHn(uvf%O|FlGVLdiw;GRX=lQ7R&kC2i'
    '!{7B6v&~@X(t4e0p61YB(7CMT^ZNaC&g<!@y%?vm$JwxaniTTOS>>|8Sn63?3;jJgk5grDKD;hzFHZ%pxfoQI{zsSQyXi0JzvE=I'
    '<TIWO+ly&saHHRPbk0j2tCCINGp9m(UKMK&XoB7|Bs$#I&a-YlH60Gp?(L;6{+&CyDXgQl8>RfyyfQdh^i){XokDIw=T&YGYQ=6j'
    'TkH9qGX2+U<aP^u*H3od`{nGYm#mfgw~KhbQcF&U*Y$|#V_vN-$LY>~mdemM`3HK(P5ss#4SZLANBfhYbD%T1)a&hC9edD8V{UC)'
    'e|bME<j=FsHS^|){ipr9&C&zf>&s$F>m^#dPlxjp_GeysUAU>`d49_iT@7xukC*wdc9@P@JACg7x;qut$^5XKEz;WF2ZL6*SI)M3'
    'rE;+|XfEEnxn#4Ls}~mg+^mw_5`Fx1H-qbZi2K#9)B83~#a^E=r=56qaGw{}-wPh?iCi<$Px+%tcbx82dzi`0vF1(xyHh$Y$D8tL'
    'nko}*zR=zB6EyEK-RHz~m_6|rg*@(VhR$m36cdZ)Vkh>y&|Gv=w3mgv|55Sp^NN3(5FJlOtvi0(7<PP@&US+HE#!%YaDV9T(!PN<'
    'UHW@U`!ngji1CPzh_h*fKJISHKhOMwH^!U>+5MzYo8$fZ-|9T|nlt*{!&{B^<Lc8M`IB-sn7^N(Jr33**T+1Mew%1)>3*hL*w>ju'
    'f75+m5$zC7wf6I>|8uq}A17Tg4`*%do%iLj(s??s$$qw>JH+$JdA-eGOFZcAl(H*Y-x@q&JiK_sUwDnv;h64zHsMsnJf_38INw4}'
    '?LlHbs+~+;TrbqbI@9Xiw4a`{S7Y)%c5_*$gfZ8rS*rF2en<RiL-&Zz$=SJ;LpIp|^@;A%jm~F>yCUwKzY%j<^L^-TvZqN;(TCcP'
    'PSV}HV2*3Zl`;L^*@$(}IUn#&oSEaT>vB!RQ}eqqcua9pp}R+Su)pXKjS=0XXkJ8jWsi8@uQBm1;;)1Ln)n;db6Ut3Xdlxq@y5n2'
    '|HeFVyT;$G@hG=o*+Vi&zo(S(iO+gO^E6MoL$roD@j$0Cc%ges^U7?APtslSX-@|02F-IuYh^m!`t*ET@Zd^~&U8-yc8+x32O6*1'
    'FB|U>GU7seK)f)UbZ@z{;0J?yBc<l>x)=;<P1@5t&T(EL{zH34_nqWW$-Fark}V0I^RTn0F<0}#OK={AWk7@Ld3jLCY-ygf=a7wk'
    'uTEzUn$xm`_Scm(VVv7?wq5V0sX>OuJeha1lNj`!%H-^N`CpR}ojdUjqBUB3jn+nI=3N$!ly&?!$w}god(d9JySC_7$pbx?K;E9j'
    '*%6J%eTt>`irl+F7QAIe=V$OhqKRQ<Pc-XKipf67Wna^6LC88f+dc6a(uJJGY=qzB>6|n4*<#VHWIfPM-=xtBJ-?-WU1+}QE514o'
    '_$sYoxg;7)OuVF``J?3j$1$yWPIs~~8eaoCl=Ksl86i4XYZSCz$tLHL-_SdVR@}w7o8Qqr20aIS*x=VJ&uM>YZ%-ei`Hs$v<{|D{'
    'Ygjr?^c|~Z8bhHw&QjO=gSoO^LHkYb>fEJnVbHkNNq#sLp{J4FLidKo-IQsK`=#JX`8_>*5#!WSv~DGLJaLx?KWY63@LYq}S386D'
    'iS#h=Ir&^b+x)!2JJp_(Zg7|t!~7}CuU}3?gBKciIj?qZV|n)AqeN?~X*r8IkbHMY|IC0l?Je3=x=kA6(wZSFJV)No!2$Dewk0p_'
    'UcFiOkmTzyL(gZ3PUX8v4<#M(7R#sP9ydn8vx)|YN7GqOd^%5F-)Hl!hvwDT%>8*`;kjLBPkP_YDLAy(nLFtrdzX}z;eB^&7V~p+'
    'T&y!Z_FI(C#LLT#t>Z-IDCD@-qXj=+o9F7!XwSa(zCU~3G4H5`e?#(B>9Ylke?@c_wa4R8CqcTWkk@`Tyhhr0;@4izbF8(kPo&e{'
    'rlZ`hJ~(`Du5y==!Rz{R|3Eixdf?55ege7((_o42L?Pc+yoKg=91rR9=yxY6$0ToF>+$J)Ze&ZX=)2S`)mo0p1{#l;pA%nb5q}}Q'
    'qyXFDO8W7|<X?CEP3vR+W%3`kD@eaK`BzWK*7IaTGTDQTMEYGSOZ%Kvd{62wWZPDu6O()<9`06Y%{2BDYYyqWS`G(1y-mO05KpIl'
    '$gD`8k#{Y7k^Bn$88#c+Nwn7etlC!k$DM2n>>1f-bK<je;&FYUFOVE^FZvz(8OagaM>>Nn=}_16m}EKc!DxbWw&z@x^0crdyB<0R'
    '@i+dRk9nxIGhZh9SZZDkdQ4?u0}@Rq{f3wC3p)n7#MS4y5f7E;M9*Mco(s<F3>}qh`VHix*n<|WnRq+NM73Y$Jn7Dm-JbWsL!_M@'
    't5=$Qg7wQ@l66&j*WOKL`QFbr{p_GxOHR75wOT)6Q%#4HJ)NogT+)T4!)iV`-dss`FQN03Oz$jb1-gIs=b*34qznH7?2?7L%gZ_J'
    'y-L}GjXzdC2AtUqV;oH0LVVBJ>1VdAkMBuOJ;AQF^c&KBuxE7FwnR^CbI=<3IdQ*&?;4w|H-#=&ZASP-V?*{rmFy{RDRqF>PuR}y'
    'qqw!Lqrcxyma{6+U^2_JOT3QsdE#e<nwX0h^P3Inmf*h|Jg@dRA>~*(MLdFNlI*vExO=1@-*N6A7mFVr=0o>8>1oT^uy5`m)0CUK'
    'CMU!Xgk8nH5=YQ-hGf|u_M4^miT_OdMBLp`GP|Fxl7{ZoA(_!49ov@8^7mw~VqP7;F6NhYU>8N7qcvV3D}I8$S^n{S|H8i6w5avD'
    'cT4Znb3ZBjXhixY+s;E}JFUG&f%Kff7v=>vnMrSwXKnc%cj?Qq?q9un@QC(lANt;#(CM*0oUK1AINwP}X4?7L6=w#UfM{6kjr4Cl'
    'zB`#c&E@Fc7Nq-M%=5>4vh<tdc+**ek4=V&@8bVSlK*tBo56wP{E5aRK0Z0mDzw1xotHY#f5kedun+#>HA>!O`7#2T2i?N)gbglr'
    '@<En$a`;y#-Q4bhzHE#Uug}H2SIU?_{Z9G&FTan^kag#6%@@8*_9d;!UfoZ;kZk~;FWLML_0|+@O7-p<{3GWX-QU>;a!%cS9{0gs'
    '=TEbAn{D0kXtE^!LuYp-dqUqe__n`?^lHAlxX;EtWq*%po0!i{rOhdPJ<!48`D|F{4E$8m&a!L{IxF*;bc_As`W<vH;6s?Dl1KL4'
    '58KRJ5F=o_f^B%_-`-E#xAV30T7+zFWeZkXv>w(OVgD_OH`2Ml*D^S<f4-7AlYU6|hV+*%>4KZ_Liuv({_f`m{@s1f_AH-`eh=#^'
    'RjuFC9>2=Z%(<0?O<!$stih=q{mCfLdZVzX`~==j`Vh|eCVcMN53y3Z7{>06){8FmqD=<=^A+or!WYbbW73W9q~DO<K1WOeKJVLv'
    'b;$Ke+0){k1J->5{Y~n9dT!dr-oSQ;e)dLtN4$ys5Yu4``{K_=dH9EvUU(t>o6c_lnMwNA6*dayq5T+alWyd>c+BfUKBPRaRnUxe'
    '@4v^`d|`V29+9mNe7%w1GJh5R)?qqI=VapqV+tPdwRd@$%PgJS**;z#6Ze?tKmSH{XW%cgeeSI1*m|#w?OfvTwQ>Kg`B}D}kX@Dy'
    'YU<1(eKU*LQQf-xf!wbv9WZ?N<-S?`BW7)(d7ad~t5?(>k^Y$$x>L+~@54G!;5#Z`NN3API))u_tEI`VTVLCTk0YSHz$VK(Rq>hd'
    'XOO*8DU;1R2fu*-RgHNQ@lE0fqqfj1Nxvfb(;5%m<9O6MJ0+6ymFwN{ly5o{+-VwPJkqfmAuoclO?e<<b+jL|iuQdi$)-!=j?w$l'
    'GG3OL-SXa?_`|rZ*K(OMPs4cdkp}Zn@j3eb0-nfs4)$cVxhLCA$W`GNptW>X^o~32ul9!;_9gQjeh=*#^HT7k%5o`UF;~P$L%b=k'
    '=gc<ZkmPe}!1fFAe(9@Ku^R2?Ai3D_<K&Iy2eIWwIIg@Ndzs@b)$wO$9I#x9{-%)8eqj|mHGIZv+DFKvpV}WWAiH2o<8Ip|Pm**$'
    '-~(v|-?z<qfj-4E@*K>#mX0O3EJFr}(Xek|GFsBzLHy58%qk?e3_5Md`)2VZw*BRtI8ORv`cH^9{U!Jmop)RNMCo&B6E6&2a#s3+'
    'x}S)#TJl-><cq)r5dUXeg80;SvZpoZJ*-FkR<<wggY1-fIlG@!IYzk?_R!L{S(G0ouvHU8SI}GNJ%bnUwD-}o_dNXXB=mN&^HO9x'
    'rQ5q&I{&LicH@L}=(+Okv)?N}uXm*$r`9fY!(lS956dcXcEq=aoqLS0Q2XB0{<2@AySz-3Skp_^{C)jPvPiFA@%2O8U5bxUFT=jT'
    '!vlLVYRlSpQoTEf*>&?$myvX6-B)}50qu0|LN4b{Zsj0+9o3xFk!|@AXUEnIc~v7l2={72e2mw(f&UP?`C=RB0d9<q{^&oZ0nH-='
    'n(y!2!o|36{ycun&(GfEF?26t_FVY-1FVC(7p%9kei5a)kWXI!hU~6S@C|Wy_@O`Eo(tPH(b(<p>nPFjwGFHIw`qGV)tCmBi0JV6'
    'b85!Dd`;JZ9#I**5WgWgKOmXwOSzRKxk`3)Z?bO;{nHG5yPK3caPkIQh4=_;i@+WUFfke*;gl6lN9)gPn)_u^$);zJk)zITmL4Re'
    'Ub%NSEFYG9H!4IkM7QvzPDVK+&J24wb4L8o*mt5$`1fB9I^OGX+?8bv(H8JO@OR(I=7c}i()%^97xoM3T605Z4#yqxv#6ft&mZZB'
    'mJgHd`uMnswCy8)0`>)x-DvRKz|U&Y4t%Rm&wTepUw*_hykH-ky~6!G-m9>`1@U^=$ig2#9!@sGf1O{Gti!xAunT9^^$)gLN6cG7'
    'n1RQ3rard^cKLfRq3!KwdODp0p63|-JN9f?TaUXkMofB1UD}QfTF1O{^$ouZ>z%}}542Z%CAa7d!~PFt(`Vr`p}oa^{IxmdBK+=1'
    'GW<+B_fFxXh}O3xCzew0Laggz`_-hMmF_rn5FWcrd}TBtyJSwbRyH|<e<STInuYZt%HQ>GgnpvpY2NyQA5PG31Uo?dXO_+j8ZmHT'
    'Z1<;|I*uddw~TMG{(j=UOyS;>Jp#VKz6Jex5Lc^|x6(gyCw{gHaCk3^Hre;n;e5w28HrPKD)S`CfHiD~Nvg~-CX792I|X<$(&b4{'
    'ruRU{OawfnL-s-WFiI&MnfW~Ni<e#K&Z&DG;1g{>wtc^ohwr_9c|1zA^8Iyo&`%7Sqh!9>?zhVQWFm-9f{z#2E=tVOW(=~N#N3I;'
    'Ca^c8|NfwRL-x=BzC+MRO5z!T&Ac;zg)cHSIL(LP|M~5Bl-IF6p`$3D3dRrOS=xrbTega#l@R{3&wl1OOsKkdQV(U>s_){abw(U('
    'l=5kPb8#mhd^buDZZop&q+iuD{b(H(BQ#^Vf&C16Nn_7|t;E?%87K7uV0~S~Cl+8}h>lNY>`>T(B;&mNdCq<`A>YaFg?-QdOz3;I'
    '|I5T8)vnL{Nl)<s6$=kc_h)jB#rFy<R+H9b={v^fW(;x#oq=rOT~s%Rt>t75|26w31fLFkNT7Mw%W#}>K7##5d}PSF>{{6xLZ`mO'
    '#Qn=@wbrOD6!Sdk6Ep{s%lkX=g{&1@GymHJy0o*}J@P#r9_Y`Wv?CE0iShYg9@uC#As<5T6TbH7Z+^y%qih@a+BqIuOp3T|Iq+{-'
    '^4pZrPj$e-vdP#h$XvcF$8qYq#GN2rFx3ovG2O{9N%yV~+@3FRG6M5t=wt$Wou;#f{}jA!1bHuYInrMR2C#L2&EQl^3ipiPnb<4o'
    '6LW)mWca9o9aHb>>wDJPO-DJl)4&t4mWjstiTg1h)ea;Zyv8=abhpgcls|;-;}yChaDPe<mwtr7Pnrv36Nr!fu;^l2l5}9(n$|Oa'
    'hTfEaIrO}wJ^NXqM}+B-=}pnYPkDywJhaW>XNhk73+tBUqqOhxBF-oM7gk)5dDLa$_=<m8Ho3B;4x!(eF*L*xi`KvGxQ%`mda;N}'
    'Eg!_0F7Ts;;)uCj;G3uK*TLU*EK2*Yg<c+`*CVb&dXB9V$KaFH{^R++h@C}wNA=)|xV`h8*8j%w@KV)V)LK)40aZF2fA2t7VP7Q6'
    'ZQ_;NM0B1)2R;Zr)z-h%oVC8n*b3l5uE12tIPPU3W4tVv5UYj!wB?Gh#pWuu8)x&TvM0=aZete6hD<Jj4~6|;+@JLnc<T!5NGUpR'
    '((&jH*gmwF-wtNLrp_vz`I9&&aL1&l3tXd&W12dFsf(-kD-6_6=$&r0d4dc@Y_D$NSk%3gacH`i6R-9|?pc=Z-Vf<_%hGwq&<O4K'
    'FpKvQpSjRo&3W%PXHmadd}pV0IoL&XzR=_RP@Fugb!+h4D(O9*&Li4|aK8%MYtF|Du+$H8BTmz5=Qs<|ag03mY+eR=LG&vy?lJPS'
    '7P4pg*{Du=i`ze?bBE$DE8xwt38GCaKP67)2k+_J=EIEOBaCH;(dRv>&+9$8YM*VKef20d2A(`-UPk8`d>*$q5$xipawYUT#2cBv'
    'gnXopT+F#y@i?)5mNhY-$Nk=nuaRA6oo5W5CT`wBUm9f3ZZ$Yd>1#2@{A{oPtS(oJ(cQ$}MdU#4Io(S>^F78t5qk%ePN95}v<A{!'
    '^1S}X@;Q#CH4ig%H`+VoZLpkKJkmu;U(9)7UERch09y)rXAFw)X~^FQo!!|eT)Pu_N0?t3vZ&rB9Tc`ZeA~hwI9L~eD^Ym;0dh_{'
    '#QQH+Zh~7m?3G+H^Q<5XL>^Xvfs<>n?9%ByakI{mF?Ivs0!6&0nDFfU0h{-^RkGhV{t3Q(^EZ!jk<2w4_ymzVP#J#@?COrto2$@^'
    'TPuNYMxK}9J2kNCL2gojS2z4{oU<ADWI5kJ<`W7VQp7Le7x5VjLiX)(&N0vI1+g{6y`YN;{~dBMItSROmS6g_9M=l%e>tnpgYI(e'
    'XRDY?s9Y-PyMivTrL+F2>`meqx6!?QY1wDjmOh2xeAWFg1IxmAlXX3oN3lGDzG>>8ww|;VI2!PMGu{$&Z<W7=^*rEqXYgewvpA!h'
    'D{zj1Ki9^a+q6_UWa+=dLtL*#r~aK}p19{d5xa|gpAK@a-UpCv{e$)+>pfo*FVBh?l!ZCX)BHPUnWH4ucw--g^5v*?pMV|H7|kGV'
    'B!5G?+K~Nk#yIjbq4UT*)r6v@NX`=HQkZKiD_@Vs`UcpF$axEX@IHK?dwjN!ay@R6@$^<6RM@6AW36PTu4dH%@!KWwm}IbLH~YB<'
    '*wjFF+1OZ;+qE_8q}%n*@klR$9&BRFl%Lx3XK$;{JbK>3KkTN;j9u40G{j3opOLINYpis49pq02zF#3*{H%4xvEPZa-fKDGIrUIp'
    'pN`E3{xRU`=ZqzxF@AB*D`Qi13~Hg*UP&T%40ge0KD-E@F#L4}UPSl`Tflj#+z0j(1Y;<_#YN_Xx9ASIVgKHicp&@n6t+YAMTNgY'
    '<f(%PY+mE?^t+MRoiA;?i^fT58z`jbMeOdsGY2M|i`423l-++MeazVRK|pgvH|(ct8<?$-?~nEZcMLvg&Ycqamz{e%8~Gf2nvgAy'
    'xLgpsh|m4$8(2%>@6U8)Y~|Bj3FBV#{N6`lzvM;TldP-i98`tBk#t}GquS1DeJuUC|B?3f>~2_RBVBUgHHIzZ4hmg#B>V%7QT`WV'
    'Cq`~?jK9vx1BQKT^SeN23;BVR+|Pz}sju5}Vjp08$on0qe+!wx`hHdY9jBj0@=Y;rgzv}c*D><-d*J(ru98u4$)vm0vgtEDU+9d`'
    'vspKYn=|C8)T8LReyW_J^NZ>r0dD83w6$++M9dS|_n0-WoRap@<^vyXUixTTjK}2~9O>p_zADAcJ(+=g;b*X4s%FRSug;rz0^2FI'
    'OdWa<;=~(~+xuY81=eZU`Wfh-pUy|dJ(Uby$IHwu#~r-S?i%n-Z{<YX+;r?y@ixOwg<odZ>RuKtvN@WhKR0PVn%%fHavV<cG18xW'
    'dN<h*tzS}?lDI(W|JL!Q+^%0N?Vs6&k^D{5F8l%?QglE%a*A{Eh^Om#wD*|D$J)7ZygCV+G`nY=4R_=TkM7H{+hj{mMLie&TN`VT'
    'Fm+a0`-E%|n&Tw(dV&uHdes=Y@m!C`F|dz19(;Bef2|IW&ascmbHM{(&n@=!-B{Ju2yAaJs3lPE>HH#9g90-BX6t8P(s^xtQ)7$u'
    'xMt0XujrhQ@}bOJuF&1GZ4A~wy`-6Y$m2;&ryeV?ee>42k=@re{;l)UXpCDc$WP=LF=RaJtd%nAyDVX|vffk9vYz)qF53Alj0<q~'
    '5gpm61A^QZ*IUHrx?A_6rexVUdj6T+yplZF{@+l%NRA=&ZaQO+<(gh=<B=UZ$ch{~__!YHf)8Vl(fTd|Gb3Ua%9quazLd{=Iw7B|'
    '_S>qp$h+vNywS)0pa->f7P2M;@@$ugH$qQu4EJZ87wTw0{{8EJ{OkBZa%6h^(B-|hAJbp6+y5i}^*@)#jsLIz^{<ax9|1*xch~L>'
    'gh~qPuz!}$&J_tZyi6%ci`pnr$8W{}+oTQ(tW2LLOTl618{;8^v6e&-C#P9Y8wFByg81c^yXdGw5`8n7I`gB}g_6^uInbfpa{kZu'
    '9-kd%DI_|FlKPbaU*({{ejGe6e^38U;b2>bF%gAR7-UtU5K=lBgfST&j&kk%w^hJ`gY!wB_X><$u06aLZtA#q%UKj!_=R`8bFr1{'
    '(oHwB4!y7CCGXRee{sA#9C(}euCvnf;GoWn_wKiTAyA7VP$GDQVD{xa?mgTSy+#)T0Rixo1hmr}Fh81)G{l4RrE|S8;cS+P+3@12'
    'XP>QavdNx>Q&#*IzxmDcQ*+(SQdtfx(IwdmfF(WCk1HZ|S;RXMub;hxjFir8JjkwS|FM==yoWv~fp*C{q@aD!#b>}XDMe0&1k`X$'
    'pC5dKj<(};%P6dq!B|^9+w?d~b6QRciL0}E`3qwwmu?}soeybUq4Aqt=i8@eA`6F+@{@6iiOsN&y{n)>Fz;f*qt7z{HIdTnBj`7U'
    'fL|p%j3WYw{>mxL@$R!O>=K^KiUiQAbZr*LM<n;dF)EZJ1R}5ppPsozmxa}p3~m1~>AkEb!%`|JHj*R(knv~b<8C_a;H>Awh~+aR'
    '#L|NU3H~DqaB0*B&pFk@LObVsJ2+}US4*YX(71`WTR!_<$f|eO-z$9Y!uM2w#t=BA{fpdD2+87ghoTEI5zhQA3GSSDh8X#Kg_Hn~'
    ')=q|sdrx@04ge0TwKLI;X8!M$#r1uSVqWb)0pg-W&f;U3O*U4S^R!s{rUhp4dI3-b{OrA3^T)mMaW+C?M%#N|D`Tnuu<(ya4&`Kd'
    'R>(g_c@$_6i9#~K1jF$|CPAx0e4Hf04sv!rooFvFdaVTr{4vjw{#N_L{|@sZt=J@E0yLwhC2wf#SAE`*y{w%-3VE@9eNOm{&Sg~F'
    'kGn|`(63xcsjX%7UTOX>orUTwikD@hn=s^3P~gZYCe}bPF&Uf#;1E1-JtN~?@BkzEG*l!+6!pp-8$I>DEB4H$q0QllJ0n4yB$u)m'
    'n^xjz3j9Fa$H<z*f3I$u6FeXPZs^k;eIb5D>ll`f(+cq<l0UR(2{?Pf=iKxJh0I_i7G~*1)>-8iO;%3vpWbtMCtrx?vD4jqUtKS>'
    'o}E)^XPtH8M!&f>E6s~j>>uCocQ^6k6ie6sy}fAm`ebC{`x1S&!1(lBi9R1Mn&q9>xWBxT9JnC?mF~a`$<b@mqj#s*G@laW>y19U'
    'HCBCowvle7CgT6ZTVB4IN+<6nt!r9@(bQIVSQVx@D#iVMjU?kN7poFHye0wK`7@HAK<~})eit(XIC^n^>5d&{9FS!i#+_RtA(;5('
    'k;eMP;L1w){v%<K`Rsm@S|;eM_9$Q%xqrkP=(E&&5LkI_q<CEh&D6-q>u`}Q@HD|s2eh8#)~(X+g?Pz$+c`NE-V0;iNpC*tB$!63'
    'os3)Q(|)OOop0||+UJ`n(%If*aV~UjL?5d*{(DYW0Jj(NYx=C!1WonwD?0aNqeti8D+wAIG!sMzNv8-J$uH@%7apI!qt8=LF+X*@'
    '*KhA+0J@tN0)?v&T5Ge1LIbS~(+Sb2OR}%&y(IZr$byag%_(Cq@<#z`mFuN_9dF4Hs$@@bJP!M81O=^oHN7Pbp5RFSXD9P=vOgIF'
    'tdGK}2mOExT>|h*a@ROdl6xq^di&^Q-chiK4EHl=YupX#+6GPW+J;H|ow3F$(in<&72)t(o@Z$|YD%Qzl_B5vkUP(c9pPOQlAZ46'
    'KzANN3Ct0JgUt3_B<%|4k4UVzi6qC%SwG`lL?ES#<P_Z9!3{i96cASQ_M!?k1xA|5Ytv0tEJ-Ho^7jbFLwCl%*^p*=2mW0_(jT6I'
    'Zkc6AvjkTz41P<x)nLO3JkTFU6UYvB*qE{o#%oOgv#t3^c_r`MgyxV~AYq=)3$(oz`k)L*NF5BoOVYoTZ2le!S{Ma<U5pQK!dlC*'
    ';2e$svdy|qj4X*f6XJpXiOxC^-09_hQXyTEcq;1%J<@>$a6*CNvf6?DC&qHkakj@FDzM;Gli9G$BHntLkJ<~;*Dm<2;vJ4Gl0^Gp'
    '6pU0rJlfavAp|DYiLu$AkvYf7QvnDJ%?I*Y0tC6Zi;@>eEZDMcxPEv~h$jnx+<Pcl?_Ggo3I=Z;>SC9{87O|?<%8nd#g~Zl;XNoY'
    'ruT#N^PadvZSag=boY>i_KbH({l=D;60qq@N3N;&ATS=j3$IF-R7G*<yncM#%-<m(%xChHM>e+kUktV}=E$EBpERCVHVEBI*g=`_'
    'yHui1_9yWoHMe)ocd;heEur%%WF`M;+jL{gg0P%rof`BxAJ&djzV{DhEbcze`kMgBDlmz49!mBaHUP<e+~;0E1HxWpP^Y;L@ch0E'
    'nuua^ir=D$0w)wE5wr#WH1$`5evfwxjNE-$3`wt%!DJ*Op;(<Np!uajc__Rv;Q(ZR(Mjfe2y}B2dwOtT$1?pEc8^;OuP?I(ooHT*'
    'eNb}v{!Fi49Eq>e=SV6H?i$&gHx$jAkD6LX5#Uv_<<~mV5(#=q`djE_6+^~(d8O}~_F44(UQ&W^!~91AXF-1}Jtx>j2@X<pK^I&E'
    'CRDi9hfEUus2I{c<(&v*#bnnQT64zu4ERQ2cj8}5F0`F$(fVtKtz`eMF<knyYGB_!<2hVVX_d*(Y@3nzpnNvUTNTd<<in~&wnJ$#'
    'O(o!~pmQQVTWufNXJp>tFU+TTbG|ii#QVB=PWl3nd|pU$Vbmx5E{2CWq&pfqNs)BP%JCSZtN-p=Vds&K`nSyS)*`xTuKK^XcXXE&'
    '?R?RmP<$@14J<xK^aH;QibIC(91>m`gbrUTc*?N-t<6P+9FtyjQHppTc)hzUyW;6w(Q9N*>ho&tJcFLHWxrg~y#;;)1QqG|%Pe&z'
    'dpcwTnzkDkcOiZ$z=@`vcOl(`c)u*3t86^MPdFhwxZ^KK21UZ%dM127=egvKlWJ{07s=rOTtlD5z2|j5vP)b`moR+;#yUg3X(Ssk'
    '5B!}yVc8i@{#LpRe7eC|s6wZrs7X>Lx{2hYu)Y?^ed)^}-B1)AMZq4Q3z?fXh?&ri!k9>wRCYH9nM?C_AN(`j+KaQ1{>mzfp$@Wb'
    'Wdlij#Iy%Ep|NY}IsgLF{WlwFXy4??DbpCTco*>=H0027k$GZOH}DAQD~7BqUdgV%E+aYv*#)pCO&{)W+7JI$MXcYsz^wDFE&olj'
    '4>DZKm?^+rq@PSU{s8|;PSY3ZkM}X1ky~w(-Jko`!#;TVmP+u4Zc67}M`BSQGG&xc2>K^|p+a($6I%@WABFbqvpE&Se2DJptXnIR'
    'UzfSDcj0}T;QoyANH$22Oqu{VV-(vD0*BRRoWDjSLF4~hzPn2!o@Ep#Z=C^76v0^5Z=i26Epn187no82h%yJ-iO!ZNkn6HM$%s8F'
    'sQ^9f)W9}3>78lv!5(n~5xkH22lEYXBH)xYNLm$|i1@LjP9}jSJg2oN@Wjcxs~NxsBJmvOo0!SsPrYQT+oSVD5~N%s(Jl%}Peh{P'
    'CYvOFaYA7vmx~BrefF88P{3C3fZnit8IT@H=RwbLfgVE+Xnj%XYDTdl*=Qy#<LGX2qU4Z$0ICq+nrI~@z>X$w3g}zt`>jAWl8gxo'
    '_XoDO0;3>?ID`K7#5b*<mA+|h$6EU4^#GvEM^E|ZbWB9rEso)L@>5|Nhddyi^*F`-5D9Z(ee~OVWpRsNgYp@}PLvIZq@FH)o3J5z'
    'bQZ8r7=RC&RDg96OSmX74g-yaTr>(33tisUC5pE1@}KjWg!W1SY%PDN-fu42?VwQWsB<=oT$8NKZYG|!ulw0Hj{@XM4^p;(CyNzl'
    'Rl^L!23G!MFUFr_0uq#8fo<t8_(HTFB4lsJjmgE9e$w8&hy0FTvthz?9qTW7m39;-S?ax);M;d!0Gru2S7qK$JU9DG+)da*ukk*U'
    'V9$-SlRl(iFRl@PkOUC_WO_(0KPpHroF}I2BOW7eplx<}2LfFP4bbTBjyKsC(1oy<0O&=$or^al*hj+!&9uIRVwy`X4vTq`o{#1d'
    '>dtd~ALCaI9c(z?s-kbuyW|}tz4MA#8a>yid(HmK&15qm-G$D1l>6b7iH}vJTu|RJcsnO_6fb|A{25=J1ie~3LpC6p4%-HuIbP_D'
    'l&-GnRr%5*d~!5l037i~6-zK<F)2~pRqrV`_&_lOn$Kp;zK&3=kM_EsCi)y6WHT)VriY#;-W6-JYhU|h8|D}D4S;!AbBpK4V9f;a'
    'a?lRPr<?@;r)fj(CGo2{7nyf(2Uc@wa~pGy`qzq9tnAwKa`(mxg$Q0==pCmwejnl<iCbf}Sm5*ds()%#O8Vb2E`s>lspaJ^gVp%d'
    'OvHU(x;e$>sWsrZTGW@wMPC*R&~L9tV|5X$d%4k`;O|s}?8~N_Pp`RXmUzC`*6k%dU$t6q-Q2BNcu7x-<LLOXHEFM7{Gpd|G$t?U'
    'AejJO33AFMIXAsy47y_>zSBraS_*wG<fcK(>A@DocooPsqHm7|M8kCEqx=CyA>n(ayNL7S0{AvRki4o}>#2Lp4corr3p403;#Vw2'
    '<9l)PUnGII!}l=GUmf_&R~ZT5mb~xF{v_u8(x-0li{P`b_$bJx1`mBbs-luk;Z@p5;7P1|Jn(t2yfh1}t99;YM$yJlVeMx=X>LNr'
    'vY{Gd(*}kAxUd#CwEB|ondkI%fAjDAU&1<Pg87r=xvH=aopWW%2|dd8)OdhL{Oa4wZaUI_hWJ=0>q+|G)!d^y8~7Fs`cXWUF-TRu'
    '1L|%W&nx{H$!U;BXgty3n6YV(#_GeP0gZo%`gDD=PXR_(z;jXXi4(V;G|f7wqHM0MSBw4eJ4hH^>f}`+Q=^!JB5ZmS4~F7Qxvk;@'
    'Z<~jO2Lu)?#k!=%FV^VZxy7TV_ji&{NbH)7KJm+Rh2Eh2Ebk-4;o_c^@tKjWBhp#L>8oa;*eoz*vlNQn^?B}6Mw1Lg;rvWO$N$4|'
    'Z(zg7X8aQ}_M0uQ+KX0dacyqL$uTe`T`8x!iKJ5;IB!E>36%UQ9b5D{t$sS|K_-@W%?;#bf5BJ*jWftCTEoS$xlY_^E|+Psl<Wbc'
    'kRIP=z4npbbu)1VN>8JIFU|Xm25SNXTEjjfF>q1Sg~RrC1F2L{prHm_T`$W;j^BsM2O-WfD7wnNRkG~|z-cBv!yZT)Qg%W1u`e$F'
    '3x2pz4CYJxvWBE~+;bF=-?smY=%J5uB3d9l<)(C~9B?DUW&-%5R;t-swwgV6(Oi{>%~bP9y3DOX&l7FXc`tX(n{x&)WWB{V*VMWH'
    'htJr<=XBpbvl}-kF88MH^D6m?J(#rR*n_xiAm_QD%$9VT8|gkbp8HVRH!8+hROe9($;iKiCtFR4cLRGq=HHDK#wR85U-vjHP%FTR'
    'y;#o~bTaELPIT@sjg<rJ5&f4ty_FL3-+k!cSJG=O{7_r2-@UW1)R5DqzvQcB+(l30(ZpE>cPlH3y8pM}^+)J!|H1P&ZKMR>&EDkD'
    ';PYxZt^Ng{5ih4ZUmmBdJKyCypCaudxXbG#7xVv5-(g^>r?g*_YU{trJ@yY=IDXT)|JU7RlE0+a!Vk*Wy(-x)tMzBN&zri>3ioMY'
    '3VXP_`4r8=ICC_>1=g*$j=Q%ZU6$qtKZ^4=-e>=xK64#U)jp87I$5H|T20$h*d8k*ULCcUH)JahuL<{-41D6B#Q?jaP;7u{N|K)5'
    'me{XYK6KzBt&9~H*dP=?CfZT!C0#zVedgPop<zYJPoOy)<I23q9F(8%;TS5n2{vI!=h6QAXnY`Kg9Q7<cz98y!uA)?`q#wU6`g6E'
    'NeIUsYvaWD`d`Dof)KVjX8g=k{yvgESk4i8gsU5516x<f4^gyU`dn+HWH-Riz}6~yi`o@?uZqcLe}2?+TlrhWN<%qi9FGg)T&+m#'
    'l-6nGN4)z+Qv)l8_!6@1EIg<z41fezU{{d~lTXn+_9AX(+nshSLtzoZaT#Evj5A;ylAsGTN1ltAB=$m`jV?Y-v}YB5o~cG6Y1|zd'
    'b5=!9tJlk{3Z4JD|JX3yTK1>uS2ARQEVM5gy9Ai3Pz<%3R6g;eET)E--a+^nr2Q_|5GuMRd><mNowv^nevhx%4k>BVcHM<&_V^p}'
    's~zu~Fk(HTS;i{UQiWo<fNwXj_hmt>d!vxI3vi0K?GlAoC#ei*OcnZ1jE8eHUMZ3dzaiOnq`geKD0H|rnqvT$tg*(TxC$qmufDQh'
    '8gF2pSq$dQHRB91_%^d~y}X}7h6{QN3fP%<OZ)c2?;={g#QO2+yLlzMoj`WSVul{XMAVq<ler!O-iaKiG8ecsedz-(qM#cKF9QCX'
    'hp&vW;nJ`56)e$K-_MYrZ9?)-H0X`F2LXTQ=CjV0-i>CBm>(B>Pa1{RQ8?|IoUjiH@o3U5M?T}+1Ami>x7zpurW4cmZOZa$G^Q7c'
    'Yb#m;zJ2I(GCb+B?E8YBl;#+U)68jI87`La?u!O;qM(qTH)8Y&G+ajPzPajOB<3CkNpK%Z0p3aEm5KYs&Aj#syMP>3#yzQAJ|xx$'
    '^seIgz#edui!tew(~-`_LV+D|KfQe3O&t~jhtoNtXewg_M3XA~9#~h-sZovoRN?ap7h^$lrnbQS$HYiA57jhg^Ba@j&o-}yF5pCP'
    'sUlY~mX>r}ptpIo_r%y+lBwK0Q{h5&1F|S4!or+&hoX=<_FFbKgg%jUxnV+H>bwHu5r@eWMd7)?JHJ0DH2SjWX<5}Y8+Dtx8eu%i'
    'isr?5nK3ZRBzus=&&{`o^Ce?{(8y8G@iQMV?l1NV@3namns0Cc!POJIu$SaJXk!F49eSVn)#zT(JtbbN{AVc0SB&N+=<m^ls`6B4'
    'J<#2Isy8FIhVBCKlfH~|hvy(M36IAJF!E6w&&FYgn;^u=Br|8AO8Oh(XoIXOrl)X5OFDb-@B`!9lB$?mI5t9O!^N}M{<GtBDYBsp'
    '+D?$;Ci&cWzg5vUiFr`_B6WPZAE8Dk))@pi7U>JvPmDruMl)Ui=g1gqV>agIy$|d(i9L+Z(T(_E<UC|i%t8{ri1-+SEOs?Ysb^hl'
    '{kG3m&C{U0LMiK%GH39`u@N((XXvxJw99hK_pWF@h55;SH|)BYajpHlo+fwuY#!Te9TY=VjYE#Gxq-7G9pmEOcjrcWo}S+_TjC{K'
    'I!hG9IdWcowF!B6YuvL-x3bPQrT-<=JSA(-p`0-8&*AC(9_Q;l$tx1gIRcyc@7ezVrxNI1boSnqi}$cECMFIBJ&$xeU|dPZLZR*t'
    'eJ2e*FbdE0cbkvkP8c@fqXLXr2Wo|sRpCvR^O*@_gn|O~qMk^kd5hUpQ#MrTbB&Q6H=BiCS6<QH84Y4gTQkAW_Djq6LFskTTW9-D'
    '*++ws{9s+K^-ASJuQUkxS03|6lTVs!mNi9m^A~~ZN^TWDQrH^toaSe0Jx4cPTS=cq48OE|C5i`%bL`o7&Gc=c0TD2jEL(^UKelV|'
    'M--7~e+9jdWFp-c(pyN5ujdu^w<ns6V;pe41N?3+L1Tw`@yWZYt=l+s??ZcXVxL+x7tqXavUqPyk<I_RuaSKn{QS**jWjCyKXp&L'
    'W<3*b$YK<qRXR&o<}1hX5z>_>k9a3^dbtlZ<n(Y8x8`#m$aNNCYBh}1T#}?Obhexq#<h=LRW7v;{dm41nNK`k@xQOFuUI&unIv>?'
    'wwGEYi^>O8#4?<362jqVT_zU0wRsWtkC>~0sq~MNTNJw|>>Nu*t0K)?TEk^(uMzQs7{A*Dy6(9#67&BjYg@pdIZh8m4pT3{dD6VN'
    'h@Ml$SjekEoC281`F=w78R8djHeFs3pLDl)-tjn20llXfiF>@L_{dvV)-&k7BpDNvlJU--75_M*o<{42dJ0@yBjFUA$L0<HZ;SWf'
    '*<!R-hCI)2&*fr(bJ2A22vcn35dVGp&jZXL;xB8|?Qsh@x6CJ4fzRq!JUr(xUh_8Yxr>&@7$nk8aW3jvtem7%bQvp2-(Q>QX1dXH'
    'Ppvzh%Z+}UDy8{*fvG&wXX)W4L4U7Lt$qlP(&f4rH>Ws0wT2I{DubOTo7n-wEParj;w*I~``*Md*t*~s&oP2adtyt=v#6aX)wLJp'
    'BeC{7-C@}JbKmkmevTD2i`svS>R`IKBVr6D-!^`i5k&<x-bLnA4-9*^6kGEw$mNRSQlHo28Hsqs_@?>$LffZyEJHUFQ-wOg%ilze'
    'E$MGInkU5gn1TB=v2Hr9aDP1SxO{hc-n%AZv(IDY;lj(?z}^;l{4#zJm7zVEf0kO@AIKk5Z;3SUjP+&G*^&<9y`SpiW!IA3Rzdln'
    'l?iGNCOFT2SWdjHN*t4E5HDprq-y#NWD(z_jK?4rrejC2kyMf5C%=h};pD!>=Dl0@AcDQ5eU^D~B8N@*Nl11ve*PA7FZ6d@L+)?F'
    'T!Dv{F5`O+7%HyuBx?GUdn}W>kU{i4eWr2k#MgjXA2NS>h7HI`Y=CoWbq!u->te(|I*4uDjk|2p3vg6Rk}J!P?*CEiHr53?yx1|%'
    'trcf&8o7=}{4?W&H^82s4kvq+LmZ+-(+6wiFhua_q|=F<QK8e}9?m%DMbs!V;?QahAsP<*)?~eck%&?KtOm`i#;N7f-8R2Bdn9ke'
    'JiIS?Bj+EZNrAZAGQaQs$nVey`+KZ<Ko9v5Yy?r?vKLdcZ#W?P$NBcM_uiZmH(ywe)9vpzUqM_kBYaMU<ti?wXw;z+u_Do^)g!&1'
    'Y$e?3^_Td_XZ{L~zdo}s<8-~4aiu>0ljs4(rW2MANfyyZqbM44rEGfh-Rk$EnQ`VG@fAPkjnZyQGJb1{cqP+UypAD@PxG8UT?hO9'
    'VONFD59>*x5IgBhg($}E(YS63Yi|X9G`7=hT$*v`#k!Jca7i-6wE0P2pgV?KO422=9&(A1NA8MzmD4Q6jRSzQK!X*o+2z7dxytm!'
    'Sg2)D3eit8j@I#h6u2k4Yz02Ou)eSN<cfmlD9Ekp$HGinzWdObOS%yLj}GzWxet4Ol&V1=`^9yV;OE?A&Z21oa=uZ(n`;H!P%Qs_'
    '8+T4>PE!8rbxZy+`s_C$9M<R)TS)2BaeVYq&70r&K2A3<YRi0~w!`0JquIIaL45^L>zH)t^Z>Xo-^|Mn>E6(F_t<0DD3N^o>fmJZ'
    '>o3ZwI9tVNq8P8g{|&nC5O$`ir%PPIGR8Lg+wJ8?G&t`5Nj{-#TK_kQ%d9db*`Q6FVHopRh|s`8Jd21cCPjn4XwA!L-l?e5q_8F-'
    'Ic~%iiLVl`r1OW)0slnNTkhRQd5gBM&BOy0zG9C@@(1}dQTu^?MUnbi9NP`(B#d)gx~Rk54dUXH8}HE(_UWv0@uG2f_Q4<rk})$8'
    'pC8}n?8ek-g4!w?ml0r;AkT)iJ#wp|qc?gb)Y+Cg`SV)2YOai(EI6o%aDR`(LE&7Az!f&XJsZbp+WPG`>LP8CGatq!Og1uC57-Tb'
    '7r7g`cOKnQl}8;%k0JWy@jUCCXboA$O0~I`jKsmnHJi97W$#DxQDb=~*^bb2le;<c!VS#u1peMl|2VC3Gh*dGeT)aU^H*arm1<1R'
    'l}jDGFXRYq$i_*!DfSuDoRRz4iqxJZ+w5gp>>Qe2;x7K5!~aunmBq1Dxg7c5g+yY8+-u|+d|r?E7Stnd8}*1YC9z+^-x%v(FQP^|'
    '*6Et~UA51OPlszxV*CU@bN@>HXRgQUH^|N!qkiQo>i_w|`TvslTh_5p68&TkpWg=qXJ^zRe)m7A#k+c1Tfn4sGz+_Zbd#cPRyU}-'
    'g4`|I+e}Q28j}Y{^KMOCmnZK3Bt0O$W96|Ldwh_X$a#|J+&AlQ{SI!huk){inkz!q^Il~{J)@w`m%wG|rZ1>p71X^!!&cI>!nGAc'
    'dSduYFZez2I@sy?C$)pjTD<|jM>I7&N!(tvW>B;?RDAuQat-l6RSSsrf%L6(6Z&8Vcx{2F)b(0KO(rzt+9bH225dCJtMha=6RwfZ'
    '7y`!ONATU6)-CK9WL3N@FlwifZj|z4b%ZYM71<xU+2c&hzOW2JEpT7RmFOM3*f>=oUxU2qc=`LMYP_u(ugbkw#CgvVPk>*U^Hk87'
    'hVD1fAp8S)U-+icxKh+b`h?C*jIWx@H(B>tj-%xN9Alb(@NoUw01ruXgf9;9Gj13P3}IYN=xUz+o#C3$J#CX@SoYKV83P*7P*T^W'
    'R`*fhSA#q0LjNOrBwh8+W3LX24rH)_jbpiv-U65dFwGUwTwUI!{cPI|)yXOr{^(jZM_9)u+LO<su}~_3nnjlnG;2jI${S;WZj;mi'
    'IkrD(|7gz+p6U-W+t9wiK1JO-<U64LE77m((K!S)x!4YVy9o@nh}(ZUFCG^dRNBV`pE1V2!PlM7aGp)I{pW4>HQOS+IeZ19PD|GP'
    '27Y`Gc|hkb^7*`Q&PMqTUL03DF|K|t>N5*lA`)lvXSDAhvAGboPHpDGJkDWY%x%zIYdtRy3K_{mBUs2?bCr3U@p&L`for<y92e5x'
    'ljtSzLHi!<O(1-fWM3bI{Wupjj7Sea9&;mTq<5Mnvts;m_6Q$3Fbc9~&^ByG#^c=vN0;=}#;~mLdoi_RBe{06S)iGB7wq-_KKXYo'
    'yWZ8BY%O}PVb5^C6<x<J&PFZ%*VKSCV}rUz4cXD_Rb-A49qB<0YLjN;$G7TBv;Q42zgtKrzR27I)r6hnxRXj2_;G<9w`yB2(IgGJ'
    'Qs$}b&~;HnZBN+dU#&fD=S;@f=vIzpOblR?O~_h2@0=6zRT;;56O7O2{xl6Q-<Hiqbu7oIB};l-nd?EIZmGb9@;uqr4##+Ctk(aA'
    'e16d}`f&(cz!EVqpJ+Gd7tHwhliWT!cUr?9=lN;>t<e(q?B{eVFz+NQM7)ahV0Y7u^!%dd&Xzr}+23WZc<Q|;F+Vb<^}g7H-=Hr0'
    '4H!q{WLov%($_y++J}*@f4Y-Am*@gI{${Wy`wmz=4?ZXK+>$k0V=-y9)c)Q`AvaFeW3%UWX|BfCW-pg$MCQ4BHU8dBwu6(Bm-WJ0'
    'HdC%~Eo0Eg6n4z&fctZ9-10rU=AGyh#{IX*o|{$Inl`~J>bIatdI&eK@=91=1WhCVt5ezI{LkE=oSU0-4J%Riu9yJdSk2LheA_-j'
    'Kk5)~pACt3lxmqSHw9%GBy&`q{oBPHhwq{{OE1v4a}ECj|F)2!^>oT4x6t@C(cb#CNnxQde91{_F6xp(&-B*Z1QYZOJI&Aw=r=j!'
    'kN|VU<8UL(628ZLJB5$FzpfXeHTmj2>@Dvj@?}&$W`%27etpe4-&6JsvDaQzIhq6ASK>GJK;?Hv=4#PGVsQA4`3Co-kmS4pwYR9v'
    'sCeo)sq0^5o$_(cYpQbXrXR7-l=i(|0`k3lBl_Lh_2OFPS@9J;8eirjcFT14vwB%L{&9}?J5|`7$cb7k>gCtHQ$1$&oUD95F`q_3'
    '`Kie6ptU!8C0>Jhr)DBvP4aW^*Q?x&eUILEx@l_}{vYtOCD+QM`FLooZvC!Md+V%^C45f5lRD<&JWO7b&0_P?EF|4|FL!TkCi6zh'
    'CEbD>ODARt_AwkL{p)#7dTX0>Y5LtBef7fg90OxU^kLuc1?DOn03#l@SPJYB*UEkUSwO!&u5-F)ybN+%R_b|u-%h&rDeV#CFM4`R'
    'zT1s$i|z{7(qb7wbMzuLISUT0OXrRX`Yyn~!|%tw96?WQ)}?&-oUm`I_UDT84n)rc$WhcalJtyu2&~{lG&epr1)az2k%)=)#r@r>'
    '#^T{UQng>1wnjnT7SX@{jCINq*UydFJGC#O=ACF9Y~ibAGhRc#E&1!X=SkO9&qBx91vLOvADi_e`dLQQV(k*06D_H|enca|S&SF;'
    's<pP0uGL*`(S1$s<@-2~y~DgJqiv|Ztba#xNX=Pbm2qESlfy3V&o6EQxG#SzV^2Fe$MBe{j|+b%a<QQU<~P8cNPR2mGB$pYmojQs'
    '@8+$&a)yD-;By;_bE&h>r;~IyFY5U`+2G5MZiaio)D7C_S^&T_4PVe~{_L&?bS{fsy)rm7D(gL+)i+>!p4<V$N9P=-$er&cRDDwL'
    'qJPu95V&YB_uafB0eyommj<tT$vVYcK(~cJrs;Z%L_@({N3(PPFo6%kKk9Ktz2Nuy9um+0ojcgjy+1N&{2erz4nBt-be>hNHR9Q4'
    'ku$#hA$7X%vbPodrryu4rkkw7OZ|2J5ak2xH%i*NL7+Rydr&B=y2s2XgS}j9-XGj6vG=mK2xK$jwMU67+^IFl?^&0g5g!lEH=s8y'
    'ANuf7U4aoi8TScT0(_qlye>Z*J>`L#b|gQ@kUo>y!dLfR$lZ*4@F{Q5^d)nSS%yYrIO+StE6G7;_d(ykd-gsM9ZH<(`lS1lj+#5U'
    'FME=CcgCA^7neqHZ1bf;S^8c`&)&#d(#Bc9&STzg*O=V}dmNJg(ho@crS{es-?-;0o~-WrCwI=&pMX;W#zN~*q>}})li0h$aT|<d'
    '#2MqB+w&R<cHNss*MZKi_suD&zNs%K;qz&|G0vLDkJi9;R>9iTn&S8x``@}G&o^p5PV74$@)AR)I^IQN`|G`!z2#c>Vci_qu5x11'
    'SNb{WrCS+?yIFH#TzO*)y$v{g*%SGpJkFUqcXF&S1YbB;H-(yJ7i$fu2P?;q=&f`|cTtSI|8ta*dCQPj>$v*Gv`^jKFOusbhtjNf'
    'to;?P7fS=9JZ$@QUDV1y81sv#nPF$$K~KhQr#a>N%D|!!4Kx1g;57<4lDT}(Wsl5(tZ%%OI_}yWSJ!ZEY}l7_niQ7mUHUmg1{lw)'
    'TIrwz5lfEfj}PTmP`d=QCh^1KeL|-Ye4cEJN9&dEFxUG-@>NTJt9Rq|In-W$lYXuk{-oC|-}7(UpY^0PNP$*GT?dXAknMH!KZYH$'
    '1zu<_d4JA5JjHxWy=TH}XrH)laxsBgJzfVfXYdv;kaOz!K(^&JHP4iF8HE?vlRW16G`5f#yho+UaIys7sataY6F!W45t5(EZz=hF'
    'Q0u#TeT}t4@OhzZ%EHqOdz9|%VsyKQd(s|pPnr__hgderd9|k*u1`&R8h9*pL(&%pm(bp+XHg@c_oh=BY{sL(f%t(*_m+)WH{>+&'
    '>ew|ng#$e&_Zw#}bw+1RcJU^g?o`lE(pkLUkax6$-Ab}E=i4$)%lhDKs)GxBjFZ09m%0n%-br0u&~@BClxN(J$63_8v8lg)qrJQY'
    'x;JRx%d{eTe91hYx;g){p{E*pA^xxKi^Y>a<yDXGi?a8yuJBz@{Dpm>zzz~ED_T-<KHB^6z0rO(_onw!VMyq#@&Xq$i0Gg{%=IZ5'
    'sNW5L?bm%Y27W8#_fm1Qua9N+rPgunkUt4{lHc%41sIgjINT=+bF<g|y1;!MkJhIN-N#vXsrMK?j6~eWm;SL1>2HXwEWC!14@dj3'
    '$9)+l6V`srIPNOzWqox|tQuSE$asB$&HM6xgfV@gJweR5N%!ImI{l3?5Arv0<Mre@{{9>_h9<i1w#)<jjWK2ZR@mP=+0%YY9r&xh'
    'S&j1xjTK;=HMZx==e#%?wU{EbD*9u!x}v}0m*;8pX|(sy=)vU>EnoiRJb|}7xZ!<JwVV=}b3dq~_4PS(j(1R#DYO^j980o(<!{V8'
    'QlBw~u1H^8_tDo6^F_QR-8`vSZoPt9z(jMsm#_^l@?ba1rJJyA7^8*`>C?i-7x?4MZaiw`gItw9%~RHOs-T|eI`H>-dEu+kHl~hM'
    'ESVNc8KQq+JC<@D7^i$E8Ne9pI_ex?Oxmm7c5p;ZYq^#a&yQ&;gE~}NPHTHtkDb}O3E;MXU0Y&3d#5noJo+AEiSJ?mF3?BwUg!Ce'
    'oTqub^>Qo+d&to$WR_!+cbFr|xL1<%*SBKMl2O9nuV|vh@k01N=sXXC_OAZiz!C%F(nFo&6ne>l_A;m;h~G&a5xrl6*bHpY0dVh('
    '@5;gN6}-1HIdIR`5^M<`D@nZ5_+H>G2NnMayp26CeJA`$b+DQYJFS`Y55YE*dVU(Q+gaK@Nxw%6IYncZ_m93?c=f96>%47(w%79^'
    '^rYlbj{jZ1v%7|$U-=#GVqTLZ@hM&37IC4@=E~Tjh>t3???NvV&vszvb?tp`a6h#L`pc7khCOo*_8w|IYeTxsc3LH#y=mL~Cj7|o'
    '+4ZNm+iB8&?0t^-j2MgjbzQ^4Hivwm_>63kWpWbOCYT@lPYs)nX-L&!>sPXSDU-r<N%}{t7x-tx_T}r@DU}uiv&+~|<h;<BDt~c_'
    'aSu$x97_+?jP&xg3HR&H-bC#t<U7`&Oa0<p&&txrem8Efz*66*qE;fu(uv*?X9PY$<kOa8aJtc6nT+)$dw0vdL5Ezw<!;Ag;eW@x'
    'I}O(D$qr)Nti=B}hV=a{c@lk}4q=}=>=ou^opk=*t@!YL1b%28+XGIt1)a91){fk3rn^4zp<!Y-QNJ(2zIhzGW82WY6TBb5xDKjx'
    'c5mi+nD>MG9D|>i)Oy=Ho0b+!%%QJiz%enfr|W@VEN(5AMW5sD#4}6a_kF|y(=@leu=Tli)@oYF?M646Z#toU)K(0n_t+ny`wV%P'
    'XK@uN`wiK?6@B~Enu%8P#4mS_moa<zEXK5k#wHdIX2n2&;ho+rdkVd?e?9hJv<}=0h~_PAC`)DsaT{g((w*Ft!N1zd#^!pd;B(Rj'
    ')BaRp(_dJ&70SxyT9M2@bh&?&_4yIGVlkiJr$ig#9EDA%-$VKdo+q9Pd;fx%1@1s^Q%({8l=pEF@ngl=s?Y4KpzpEji@AR658A4j'
    '9QZitxZD$=gL~lsBW}u5iJOn(frigY>QT{WU@yEY+-l7C@GaBbX|)kQBU)uUYPKC5X2l2(A^i%n5xLU+9cXP#^f0~=O&IrA+p3WH'
    'QdjAh)~E%cbr3`M+_4TNbe8*c__C{4n#XZ>{fFzl-s;`mA5Aa!OY1zTEa^NY`fmM){0-@@&E5F6r)T%5O}%Sie%@k7a+_rI{?@oV'
    '`?|NgMf9-Z_};pg7IiOoa|%1HH$e|?dP_Cd)g}HTzoWfe?3#tE_>Rtx-g9kK7W;a4eNc0B)9C%WRL?9w3W$l6j#I%$G|zzS=vS6p'
    'Q?|8Un0<Oh&0~?9PBIPkhC7)C_w6QG0lZRy@kpc-B#~RbM^C$np{udnU>TS>%bwl>>mhOCjAg652Dl%Iu_WGf7rl^^R?S%xm(6%^'
    'VC8c19n}_U1V|j=e2@DGtoH}W)!EIeqZ_6t#*`rkwP)E03md0VVa$p@DL=LyoT1RYm7h_^o-O&KY^d^KR>6COZXb<3OB|~&^ECpW'
    'rC5iK)wAC*=JOzi&%VD6V@FNfBhY!Q7#V#0oi2PRjZIMRTCQ_%#{6X5C484)L*S0T5x?@lXQW-kXAhf|^I;3<Ieeuv{>;uHIT*H&'
    'bWLIFw@>y!>!o_`(@GgMOLslv*DLm3i}_t8UO3a9rJ$#<9d&@+)!=yxd&k}2Oa^!OT${uG@vZnEX1p0}V5d&YYVL;KQ#kyJwO2GA'
    'B%;ULm=0x&Cy<9=)KTYuqX&ETV)#vg<Lk4Yr{>Q43LX5in2wsjEOFj8Z0YInf_x-lkI<dsya}lfla2?!h`i?p&z0k%F4ynb@p3+1'
    'czwZmpg-v|DTJ{_;X7l|c8m|F-i^IC_>6PXMU1p;(?Kz8t1DkPo-HlIHUsM#flo%`?;d=vV*Cq7_{=#bXya=n{Un9|$Jh_)LyF8_'
    'VKBq@l;cTk6Dw>T%O&un40MMw>dVLZMjY;~z<!Y+u2v|kd5}(c1&@^X-t^ZCy;=E5bZm%wAJ5UVF6ok9X#XysjoyFGy8(}R$h+;c'
    '7k;6hsHMAi?0?6^RyA%l$b-76{R%J;^&9F^W;ckX)^Eb^9AFDXj5WR=NHeJYE`IxrfAcugRKg4L$#&|TLUS>4lZ;p{$AhHLOUH<W'
    'zI%mV-0_^no0s$4o3oFlHOt?(*7v)&$?85a7A>gr4EExi6X;wbo)+>`T6eL(^k>!FKYA{1Y}{MrqAk%2iTCZ<9To369)TIBJrVg^'
    '!z=eFn5D+Fuk@}M*&_P$9O(Opb@#)y_Bkh$_^rUa!1iZc8TSF$qaM4&%?SRTdO0~k9>(|Z9IQMbT0<vTBk~k(oCC`E+$HM2BEOSs'
    'H?yCokc5p!y4Qr{MdC|qwDMsUkLMiH%#vfHGRHLNx$xqda|CU+$zGVH-9;yv?{WPh75nRQp0vaPa8HSF4hHa}s9E((ymN4pIV*-v'
    'sP+#v3fut4B78>BiHah|ur^~9arAjX--8GbP_z)e7lIanCj(Yk(ZX$cr~ANm4)nD#(*o#}^9)0@@nXvdJX7wRC#gAbQWnpae4q0_'
    'SYCEn-|LAw4>ATB#GbTlHDb|tzCTONxkd>4NU)c~*tN6X*;L~qU&O=*88Ndse2vIWWo%=C^UG9@w2U3t^bvVCekW_T#MO$h>UczG'
    'jq6*4>eI-c!wL9VC+1k%*OM@5#`2q5v2Dxe3cq#j7xYjY8%lHA97(6WO54Enk>pIdX4xC;i?DsV^j-Ph13rNC@R{_RlbsmW5pT%r'
    'CYuQ{Lg>;*F)tGf#c_FwskCAvitqC|hsH%LBr+!Lhx(g+RD;TEScf(CD`8?G6oy&lT@*Pk%j*s>VeP1XA-)s-i5>eDEWJdmON}dj'
    'zYO~|zBZ4F$Q3gG7V#t1vjcW|Ugqf|zo~6uTSP9Nv;jxqHF4Y^MC)tV><J~G`<#Qmh|HDmwT!!p{nzo^I6f9$yO~3XyT$czSkGV?'
    '8{G@jhSN2{fl1pM*ge&c#9Om0ZFu<s&LNzG4IhEd!|vKSw7eIdW6tlp%F7OPomZKgAJv!GrZ@UG)vL{YP}in|ymp~qtPUdgU+SJh'
    'uUm*dJcez-^?R%ErAK8LYGtcfWW3HH<zV1b*76dufSJH8-evCbr~Q5!8vB_yeBn_$=>5iZH_Pn9Eb+WJx36A6zx6WNY<=KgU;~1$'
    '?fP;~(vM`@A5U;_F}S}+I-%0F_Hpwy^BkmKBe3toa|~f(Y#ev?HZLjpz_Cy1lR#Wm+6vXM?V<9mMZJVSlcU9W!l8lnG-8ROM_`b{'
    '{&hTzzAs0e<LWu_xfycq0&mFqW^K}g{FxmS3&o}_xz<y@3L{3SKYNC^407j?|0m*l(v~@L3|Gjs1K0W_z7&yt+U{=shM%bg-_2*w'
    '!lx61<3+D7e=YDtpT+mfz#gz||3xf-h?UFOePiR_iT9nRz@LisJ&VP!*f(a?6${7Z<ru|F)+w$pao=-1pT94?G>cLEw8>XsZv%_Z'
    'IVYT}&3>xWBy@Lx6`vRQ|LiAwW8Nj^{SkxFX8FUhQ=!j9uvnhPVVSiMBQj2mvzFs!IG?V~7%+j`d$5njnCq~d%L_Yb5w+7fzizVs'
    'AYNWCmiEHd$^V*tYAXrbC@dQ~#y-yx|26tTyzB~n__}RdAXHCr6~)Io)uYhS<XvhQy!2;J>#YGcMBd59mi~`;XQgx)du#UnjJp|Q'
    '?YW~<aZV;}K(^B}qQ+Yx>A`o*_t)khCgu)$*^28D77Tw=Vflma4$VvCMu|GRQ<fname=%-BIhF&l<z#`FAVgY`(qs^=k>w=v6td('
    '@4UCew&C07_$;qK{*LnZ<~|??Md=v&Jf7<ssB6VI=Ofp%FT~N0rC&s7>9>6eG!OKdM(vMzA+R4~@D4xN-;H`g8~32z7tju!9cs^{'
    'mR+F(G($1+Cw7q1jX4gkbmL{j=Pvk4#J?b9v_0RGlGz4dxPK76_L288GWuDLY&^M=jkd16RxwY|gXwcObSVP^M6@vxcjN1M;Bo!A'
    'J%!~L_#9(g=>Dc3-o$vReQS;-4q4V@@If<HJVowVk1<(V|Kk3hJ&EC{2Qiheyl+qRq2=n=-b;4C#_-F$)pJ|vtNY}ABL4{Vexl#l'
    'c^D6MKNAOtnEP*Gbm{#9(-Ovn3i|E;J{I~x9lEG~8r0p*v{XHxdL;=g3F>=?@{X5^*X?BuizMk(Q5hKg-qyW&K7*bfBecF)AI)%Z'
    'cT?r<#E2)WJ$`0WAV+U{Lq7LH@_5?c`|C;C2Rp^jCtn@MjIWw_qBu-LD0UXb@R&JlPw-!YzkIodg6v;?5qdUoFs8qpYiSz1@h|a@'
    '$NBa`H;BX`!+A8JJ$YaYES7WVeyF`eGO-VvgYLbgHP*un-(!F|TWk8;IliowFR%eywi98`RoOpvoezDkyVfmt`u#HMtOY(_%dZRD'
    'p6Fsc6tcpB{f+ys?$GeMo2AKawDSzZc|KV?{;si5q<_-c4zmVs?kj8S?BI)6wVPbKzR#WH(FHu$ssmXmui%46KVG~3HuBHl6Fe-q'
    'uP)cZeeu4M6NR%RKD-yTRE512s==Uq+;m59@990jyxl@^M2kirty$Hu?8tamP&eEqeM;gw&NJfOd*dt~@Vp9Y0}=h9UJ~ixj&(QV'
    ')@9=neq(JR8}-rp<UAyPjQ<7}Xss|7%`V#vW`B+gJqJ9~U7Rm?m(TSJzjD4|8(}~+$-ZcgV`M$fZSkV@MA6G$<Wu$$yEial>^Dld'
    '+=m-InqQ1OVom@2{l_i9s$!ia&(6kqvV3c++FfNDHzjIy)~mta5A&U2Cvy&M_C6h{{9>;6csFaMOTCk03$#~znY%3X*=p0OB_6f~'
    'o&FPiyTH;YorQGyRt5dWVV?`EI%8@icB<^TH~G8b3**~i>%`#Ozp)K%@jcGX*XPpNh(0EDfit&#>tXDuafcm|8x@YX*gV;c|1gd7'
    '87kU;^jj^j<K(;J%Y45GZrJ&u;~fQwA!A#LeX?wm!Oj4dOW-cc2T?DRv1HO;*i?1F&Zwt9BYlndBG-g-tMJdWU(<Sr=*N_YZMqnb'
    'xK|F>+Yo&oQFrV``Dlf2t~%f0Gp_F`WQ?vw4BjmA4__kmiTYTx)b%i+F_~W~Ik!daE|LS~I6o1sBU)D}_*={Hc8o78dzh49Ka&09'
    'iTo5A3o<Q(I2-p&-AoR%^gK^`4#_gdj3<5eEZe%WXT52EUEHMMi;vM2u;(J)iX3R@W`07-W?j2-Eby!;qVJ@ex@OEcj4h)%eula%'
    'cdqwh#i1F$Cv+r%dv6*%OT{7-j_N4#BJ)c+%N=wyu8GFIGPx&E0@y{wQ$;PT;C#dQ=omlKR^)4TW?VO*m+*9tct5eN<2SO7h@FS}'
    'pTtOqd}pX730-_MNIT_0w^vw73^i=GafrvDFHI)!`J(642)u#jDstXcjZ90o2yodvCTJWzG)|(XrNOVdX50=wq|TeD-MQXbeuP3z'
    '$}FRQKp<PJcSrAD=UlHIX<rfN2|jZRT;muq^F7f#>fr2gw@^dT*(O4IpQty~CZ4Z)Np-e0)HK*32Y|6oz>TD`s7;mlAo^%*xPQ_H'
    'm`(Z}>J@M<E%Ax9`ZwxoMf?gC);CZ?lI$>GHYE0o^%vCCP`<3pX_o5v1Jp>D`b2L7-6GTP43_;-BJ<uU_4iJ6yjb5B(ZWOCt>k^f'
    '(sMZ0P5kh(_((~NM1KiPOMZ+z>P>m|(c3d-v;nNeaDcqf@6BHS(k$i<w2v>-VKO=E!yeqF=(9`H@GVC27H)CxUb1~<)NI1<Rqeqx'
    'V%fAesm^@|9pd{(H_3IbA=7%$nKlY*PWoZBCNaRGE+Og*B38$^M&!yc2IOMZD-?dm=1KcsSe6Q`n2ec997wEPZQ+B>Tztnv&tZWl'
    'ipOo4dG}%eps0x&*F#6e_oBED_7#P&ykT5Mpr=?^jHkAO`Hq-9DAYKQEbPDL{v?q7!1Ws#jtFk$t9xCjz0K^}2L^TqxS8g&TH+_C'
    '%y~IWuH{O0NvMXatUV(AqS3lxOmoUt7SLU|R^C$Q_w|aeCq6&MDa_#`KhJNO=KC$fb-*P)!^CFmJctJSSF;DMPiEU}k(>#u9uwId'
    '^!L3F{ebMQXpU*??k2fU8TQkzElTnYb9B8daK{_uLN<`IH=H0Bglx5zs5Pqf35_lK<Ij#c-8Q$P*HYX(!HbiONrn#wy>Iopx(mjR'
    '5FbwAKGWZS2yE}8xFPU)hp?VTa%6xzrTsS~3t8sbb(Z+I&;eNHI#M<;-Hh6((Gr%ED>|bA$;uz<w^LDHOXt_?y%@I8=QHvy+E=DG'
    '5hs=FG-Qm>5718vwwRDfh71$)QMq%X_9M-0kJ$Q-b%v7o9j&*i<|1)s_jwhy<eTC9?A1lS-2;Es5`Gw6D@e*HsmDCQ^j7u(t#)-@'
    'Z$R53mO!?`#1~kEy}$=NurXDQ+ppDLlFxdU{vvAwXHXj$XDMjAc+g`vHX<&p`yyywko?0s%U~?z)SSn{2Gi>?;}x>zFU}ox{e?ZC'
    '{G?Um-GA;(i5^e`1AUr8_%?6NbwMBaHpz}EuXWv}lBg|L*XxQq*YX{4_0Zi7_!{FjmNW2@;M}i&1kVrVs9`!q9!;=*Tem8dqdZpF'
    '_SWZf=vV#g@?!|>8`+gr#+))A=?Fj0&RJ_-gqZhQ`svtjFqL&!O<ze}^q(euW~tA~<~LuhH=*Bq#9nZ|o_V&v>1(!m%Kq7SpXA(0'
    '{kyWf0e36?UD0z6WL9Ln2l7+#+V(6>c0?hP|D<F|+7<M6`^p{We&oUV=-)OrqJDc%)qzv{J_2TVaEZzr@Gs%N{DO>7J)aCLkN$le'
    'u5R@d8~31ITNpcI_C){69A~0$fRR_PfB&U9n(q_!lH>HHh%P{TFggE;v*X{z`J*JJM%4FKc@h=yIp-w%V+C<?ru)zs%o}PY1NWUI'
    'ozUoG5LpAu&uER4nEHVm^wS9TnB^VW0kL%xNmjTVlg=IGbCEMvJ%Ybf6VkxKsNb17NccR}GlNm>5cyrK9}qp-U88TYz)eTi8j|_y'
    '`7j0~Iv@Y0;#Wd{jK!_5tv->zxi3!W_s{nyG#`T>THoDbZIfs}OG~dK8r=+3e-&K=OzgAn;rZ}+t$RM{!C=))WcrQZW~{vkc)9fH'
    'R_8Z9OW?D0%}34GfTshG*^+&gX{h_E-xbZZoTqF2es}e#p00(v4$FhM{BnNgVa^)Mcb3PHUFr@p7M18*+OJw(TJ@D3_1m7}H*2$Y'
    'PJmG_NsRus$vw$C!!qdt3yraFa2+!DiGI4|_aJW$bF?u0I!BJ<5G;SWhF;|n4xPvPXYltn=AW_9|7@N?FgNIrec{*MeWYc)`Yv+c'
    'ME;tf1K_)xy%J(%phw~t*R#8#@x11Rw9E9QxBz|`IX(xvs|Vp9bXLtuJJTvIUQkbBo*Hoe7L9Q;>qv)qm&ENyYhX%R3B`U)j8jL('
    'MP;p#FVuGWtfo_=@QFSVkF}4<BY|H>VMaub(=*(M<8vMp>qv}4i{a`20nERdBck#qR9=PfsjowO9*f~JbMspn`djFwr9hXka<%__'
    '{*F!80+XiqmCjh`6a%4`2Kn|9zaE||>f4nSUYv6hqV?-Xc6}#N!#>_m8B_OE$=wTM@v6`BZBb)F>GI6;%EwP}*`Lw(D1_^DMgsq5'
    '_)p_{C*Yo{IY;tcBQ>pXH_NQw>_lFB=RUmW=Z#`15!`*5A7t~g&2-c$z(+Z$Hg`S7Dt4N)&0K$`#v@ztLN@=du_`6&-Rlqd%7>fm'
    'dDh!qTcgDO6FaGEVJM&1@QSHH6sfJ&6lZ1CWCVZwq2r#=>xb9rER{XJ$=<t0YzMyh@(0~xV0YWYOa?tAk)ImW5phq=9@jEa{RoZz'
    '&>hZOoe5b{*YUqH$A%NL)Y0d@x2Ytssv^EC;>PHKMep=k2UmR_C+WdWVNB|!WWHbS)Ow{sca$i%yMt__Gg$A#^$FBmg89{SEi3dY'
    '@Ab>=LCJ4+2DP8<LB2Lh9LvKI{Cq^GmBAl0uWXF(Q}wAc@cyFaT)=PL4flHN9k`F4>IpZkb`oy2`Mq(=rstv_++{BIP4;1L5l`@M'
    '0u%fydVH3#kAs`&rIp({g+Rw3Es%S8z1{wLAF!ByUff$!)r=79%--Ca`)EJZZ&_#W6)d0kF3>ab!TeI?%d{KqlgYVLx9nYw*BFg&'
    'jr8&R&u;d|M>TQ&Nc-8wmfm~MqV90ERz0dYfLHf<to70V7$p~toR;6#eSAYbp`Z>p*V|L{(zZU&sB?|>IFQfx*>1ibfEE9{)(#tI'
    'R^eW+wBCJ|*8jrmA0<xHZGQVs_vfRRSbwBsUQ<7y71W>lIm`vQ2h}6JXDROass!C>Y0>U#A5YU;h5fL2LY`{|d5p7OF%H4AbFpcB'
    '=VMsA!3RDS*a34riYEx{I?crx8~ODlH?PUD=u50=z^QOtmUu7e6T)YQUc^4>iYtky7rlI|&Erh;sXYkYbA5V1uX2u^o;f$>n_J#T'
    'sk;XF{&8iQm{;@nH}CaK=O$!fRqT0VL-(YMzMOgV>I6SOh(6JDW?Rtg5@(qC+0FdnR@{H1zW95$^CO-|`Pp&d67)DsC6^!N{h8?F'
    'd$Wf;r=UhDbcDB!q5=DJg)55s;MMcX%y?VdPq;VLz?ZWB?^wSY?>JvM5&Cs2ng0y^ddM9>KWgM7?M}^m{?ohMt@@rT{ry7L(;lqn'
    '=v98HmygeA=MWyFFL|z;4C3R!+VDAd^TMCJRW+{4oWn3>KVz2k^9$LIuOjcX%J>PyOl7ZU#5J?hFP&d9J`Oh0FaumwAZxkiU-mX<'
    'jMd;sI(UQTb5Zy#)z4bS!xvVZKw_#y&qC6*N6td`c&eh8ZFxUam?}}*P3;ZyU*T^T`NPlh1J$1Kp7dj4TalW7l3oT(D`nn8VW$Y2'
    'I%MP6cG{EQ#^9oy!e{x@xvi)nz~iZ!8X;e!)NM)ueGA;?U^TrdOeg9H@_9h+C?62_B%T59i(a>)2jfZkq~307zt>j18SXz%HYj68'
    '(bpPwQ3ZA{#(3Ep_P4@;>R8ZF-Nk{vzlS&(*NE~DgWp{vcSP~<QINxE_)?aVPqXbL|IVOB;+A!zp`eKx@_=G!#mEVZ=pkGWk#R(}'
    '?yT0^llAw3ErP9rxRHBX8g}!%g!+#Hvy#{2*6#c0yR@E>+nRf2K5Oy{;~iR7))gNv<lli;ft;*&-S1((V&HlhN5eXOfU*5v1IDc?'
    '`i$2&Pcw^pW*78Gc-sQsJwRLw`4;`zEtI>ZWreJ7VB#XzgGP^Wq#|ER`C>!+dvHpZ!&h?~tiG#3uX*@9z8VLEJxlyB2_BuW`=Nzv'
    '`DvO9?AJKlvh-_78L*m;kb^RiJ^*JoOnm0kxqgy=?4zfo<)2ac|8J}HVXS;tre6#71}fL0^m%#CJ->eIwO`%}&H;Ihvr?99&(?lk'
    'U4L(^*0)A=?z0_H+})nl*of3J{4JlM@_%H|`(`bC9l4#N3;l25GdqwR2bS~PCmk`y-ZaO<{Wt0eMB~Er->-UF`J2#BTh<Cqy@c?S'
    'T!XqI>Qvh`IGjSnM*zHG_!;Fl=6V<Ph;KIRGh|=vyTn%_$LT?SVdOj>)IQIEuH+tGBYxDMA>T<Tmudf>$iIA8mqhqFmTuZVjc=CE'
    'gKg5Dq5Fz`C4Q6;eQ(}}jGaFOIAiE}NdqIC8H&1&T$><NQ<HUo9eA+B30QqGw0}%v+(cb}jTh`&d}C+i`abeQ8TFOSUPy=^uwBja'
    '&E|=+o?t(W7thCy^{7sRoo8+5P{-FjmpDM!rr?)4ZVnxy0GWUoC+>Mt)Q<|{wN_22Kh;O;3-zF!b!`dUwDt>g-kW37_;1y?$$7m>'
    '7BL0*l(o(jjE&zH$;uh)cpA+)W66cld^sI4c6m8bbwv6a&k@Zrt_1WK<o_{^?acb0PN9@lxrTOaBlagP5u1wdZ}6nIM1YwI=VU+f'
    'Gsfg<vphfAI1;wcO`K6u$V$4yq{G6eCu_>1<_YPc6IrLO4ZODU^J%|wV-e5yP)`7L_omz<eb5tqkss8Sr2E_9{!&fGT1V?B{UbG#'
    'p7_Q?_28_$IRC^rUs)S2RA)@pj4^BD+4b})+<X1zRQY+ftAhGw?2lQhx*G8{BCNc=tcdNR?x)hD^Ktof5k3UoS&yMpQEQ9w$W|T)'
    '*Eg-k%IPOHhV3~7xyq((7aNlwknQD(dWo;%zKZ-J<~vcl3%=!yo-5l<6<K>;*vO1A*R|s-<t=!vs!<0%L1RvMEF-4H_88a9_L1L|'
    'Ci(fxtlt;rrLi?D=-hzA(f)KkXUEo+0*p2=z@hpxq(2NxN7^IgA_E^ydQ`Np_Jf|uqVHJW@XZurdW0MOtF%ll!H&uX{csI_AB{bI'
    'ro+kFS8LgOq!8{w9gT^Yv1%7~P$AlzR^183JKnpN%r$$mnKp>5NoruO9>k25zDK+;iT?DKJra=%k(^r@XAXLraUVFNhnbo89jeW3'
    '>Nz1igvJJX!sg;UIxkws1Lu>ea8JFP&M#0k{r`;|aNN1sM#gzrZgn#B{dr<Pdzz^I6*Z0x`f@_LQAYIeGkEi-dV<6%1@R{1{-tDo'
    'poPi#bNY+jb2g}bpyu{l^$)5KbjISV-LulZ+uN_)?Ygf2F6=7A-5EEuw(qdk*+m>Z_MS`KJ=z!KDZW+o^L*Ne!szQE`$)e9aU1EE'
    'G5fi#{!ERz|13|jY~v!=wh;Yo8S`p9XJemK{*&s-9gXov^Y*_k2dk4k>4~23Sp>O3q(_DGm1OQvJ6w}i)>?j`gV5i?9@V)sd))`A'
    'kT^EFfAfEB)n7vNkHY%s?tfRcfkhqcl9?NXzEsdRS@zRh>8{ieFB0{4iI2=~`MvHb@lVY;=qt$c?*8TeRslwmzZ-OjXU%`3pWyg7'
    ';rK%TsPTxf?-mh!40O~IzoU;HT90~H1nYX(PnX{}=&PQlL9aFO{wMg~z-OlVYYSYjUH4hr;lW&<)g=sSnTTEs+>4C$m8IHK<UHPt'
    'e(>Sma60Dza|?dIFnT^en2VJ2bYBimv5(wI?I+>-MI+#nnighK?ceNS{}6$djKloUJVhPxk*?7%>bFJe=7xP5K@Chp&(HoB^si`6'
    'hezKjabEgaU{8RRAKW=NXe2RaRy?aC>#VApts=)s*Q|{6uox^SRmRsp@JY38A5^Gkg{cFx4LXd|@hlvnscTBTXZZvDxmbrN%UtK8'
    '$ia>HN7dLWPr5|*awW?(u<O;MHyI+2)IYnc{f+oO;^^z%Fsu8Xp$`0bG$8&bdjX`9=NaSyWHNG=Qit!zcOzP}@~K0;x0mx&dC&bC'
    'hvoH$sH5>!yN_uwuKu{teIowoM|ib=zW<E&M{}))2Y5j6UwJos5&KBuV<T&L>Qk0`{Lr7wIN*fAdqcn1xdmLmu(f*@PmS?M#rjwS'
    'y)@3R748$Vj?^jotXHIo2WGw1m-xtnluw|+SbHnFKgJp#*WZ?VV`4=u40N>LXL#&~_`;#Aiwc?=buWu%Z+vQXk#Aono{YMz{qMrA'
    '7-YXXr;o?`xIs-DH???Bdp?I8!<Df6KI`Wh{q1CP%^(K!cuk;dfxCTMmH0ERUEN1sD|o5IUaV?aJO6-eDV%Hd3$eK%NBBIKz0E(*'
    '5t7da{90g@e$S>*I>A}vbPXPX@t@d#M9cn~eSM$wF;u++feDiMRj-2{h9k!l_fGXW<bH#~&LiG!`RqVHavUv7N~$knB<>YiR~#<D'
    'SnKn8y&Lx^&O=~K>%G5ikNLfykCm5w8N<1mvVW)C7p3z;_k*oUJd$+n65R#WKisI*!niihp?J7gR_{jD1CQ)DuF=i)(b}qy3D>6J'
    '`UqUZ$Ul;fxt<OgCm?#aqW7<`UEVaV!|ECNqUvMh!!_}w{=<2$vZpKQyz}M9i0i|ifF%;X%@T6EPRMiBy=XxzqZZeTg&q3Am>$_%'
    'nf0@zuWM-<z9uV16692>`iViEP}I4Dj_7lZ9Mo51o2LsbM0dGW^%_Ob%yn4C<9Uo%LOi*#$(-lF=ob<T<Ot{<T~!&cKyTBV=+DL9'
    '3xBj2W2JhO$bT1dqIQWM<M(^finEXH(`x9ua{oBrr)1SlRrxhR?N?KGk+Ik{_Xz(|O;}**(R0GBHvip_zLr3Kf;K1TDeKF!22*jT'
    '@MWlp1HEF&wc0DmGs(V#is`gvZ9~-C!rlpbVLH*aP^VuW&Qd=2wGv~$q7HFF<Y{TSO}uH4c=NtmPgB%bA|5XBGP<tU_pjQ!^G$Y-'
    '+}e8gqRv_PP42s|+Tkf)S2wBZu6lJ{vu2;Iix}B!BQ0~}i!b$$TYrIEI;l@DYNJH`U;p3#56(VOUj'
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
        print('Discovery mode update already present. No files changed.')
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
    backup = backup_parent / ('EK_code_backup_discovery_modes_' + datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
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
    print('This updates one discovery view and the Nearby template. No database, media, migrations or JS files are changed.')
    print('Nearby still considers only the existing first 250 matches. GPS calculations stay in the browser.')
    print('Stop the Django server first. A backup of replaced files will be created in your user folder.')
    answer = input('Type APPLY MODES to continue, or press Enter to cancel: ').strip()
    if answer != 'APPLY MODES':
        print('Cancelled. No files changed.')
        return
    try:
        apply(Path.cwd(), Path.home())
    except Exception as exc:
        print('STOPPED:', exc)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
