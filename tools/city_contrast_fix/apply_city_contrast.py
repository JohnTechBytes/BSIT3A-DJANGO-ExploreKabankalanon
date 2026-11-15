#!/usr/bin/env python3
"""Install the City Information search layout and contrast fix, code only."""
import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import tempfile
from datetime import datetime
import zlib

FILES = {'templates/info/city_information.html': (('3b47226fa750eaa88968caa00fa31962196ec8054d79a527a530ef37114b1b87',),
                                          'b684c5eac18e9636ed767662ddf93c67b10b0bdce2b45d20053dcd35982596bd')}

PREREQUISITES = {}

PAYLOAD = json.loads(zlib.decompress(base64.b85decode(
    'c-qZfS(BpLmi{mIwIccoXq}`Z?t`<Kg6YKc(jky3AgH$-p`-tMe`{|*Ff}W)>QqNRoTw^A*n17%`qr>H|NW1{YrKn=hu8f-gU#Fa'
    'pKfqS{)_(hBVHbY?dCuHLmd6%KmYNXELOJZ*KDJ)c9Uk{_5H{(7AJS02Tnf<O>yYE;^Md*Ob<?5Sq;tFGyTTt%f8)irCz^RTN-Nd'
    'xfNedmbhPe{ix>j7x-N0EX`>{=|)F8mJ`RI>*b@OK1)hhue<%r$&K}qWej~MKKM?*cVuhAdh&bS-rI`h^{Xz2xHiR_qc>CAdHuz~'
    '?)Q>q(hBK$BZHpzba4B<jXi5c%S2c&O)YdJJ90PcL$*&mXMb46vf##z=yfL4mVNzToBK%V>qomk+&iN7Luu=BdqbaP{~l;RmS*b>'
    '@;NT)`SXjf^tHWZYU#^tnA&Y2U5e3J30hn1Eq<9PA@;p<0wHw72FbdngpE17W-vYBw<l*ajhxNoX(V>P{dE5ulGXIh66K?Zb$V@*'
    '0j)1OTH-~pA$Mgn-P(o_jRZMx<KEG3H@041*egMP?Fako+b2hwMsAe<7Qb2iny#Sp6V{lR($u%b%g%|JO;qlobfLe&daraFku42R'
    'Zqj<OL~Uo&-uk`$PoDw%#X8?CNlQ(!7t`}-PcMCX-hPEO?@2G-Alloe2D#|9t8RvW4QC}g7B$$EoWh2pkumk%cz>k(4oS~5<)^yA'
    'n$xA>9ZgAVxR9YUWA?FM8V%UZFmgJz0G~G;x~{KB9(-zv&+V`l(0%Zo58nxuwimjRdcxk$@U_IAHR#_PwlB$&)v%dpVfUhTti#f{'
    '>^)N>88F{+liCILMf-|iC-7rAWOh2)(P!DeTW8DgBCNCaYFr}bN0aRnU)$naJ7{u0!*k#JQ}alEV~J4>K9kypmOZ!im(ri^T&V?L'
    'Sbw+UOZ3_y8^E7!LBjgZ<BgYCW)s(WzT4T>-N6cf7a(VE=Y-ot8?@?5r@2zo;hBDmHLYNmCws6yx_F*F6V{eF{4t94A0uOT^337U'
    'HVc0~W^01p?bFC?!R8h#T<b&rv6BdF&q}*Nc)<5%YLO*Pcks(p>33JJNsDj-GVe9Uadadf$1`K-t3FOzu-9k<KL+0D2RGe?<jc0H'
    '&>qOYVO!B=IhcIcI#afO$ZKuWJ<@FhdtIq>n|%)1Ca{%c9QMwyz)=Uj0Y3}1xhkruTf?&g%g}z1KX|aWaiCt*uotM|`Y(nTu!(V?'
    '#cE#<?KwRkKD(J5Afxa0e0w1|;vO;K&B*j3*yPshY(=#L*$<}C>tF)B)PaXXvbU2H?vA)N!f)h~?kj$97b_pyNAFe#&=>P_tWgiy'
    'GdJqWn(wv@lLN9H_<juBVK@n_3Af?c7)Im1D&CWa-BD|5s+Q#eiCB`|flUo+&q^D%E@Ew)a(rOA|F<LQi4*J4e}<DWU)!ynSf8_d'
    '-w<(cqkFJ$U*O8oBR^-q8G6d#s&B|3TdUfz;ziv`E!wwliHD5~**fv$yOKtMJ@-Q`#P39T???(h>z>tcak0ayPdu>qN3w=JXo8yv'
    'B5ZsI%!+7jkVTEz`Fxv_jk<W|(wMBu>nN_72`4+YQ`?+;S0!d+@~>b8<W4>h{Da;HT8O>xowjg*Z*P`H9sVqz$DvYV_)ym613g{+'
    'xs^Dgy(8`cU(WCMT_eA1H_u8Zzb9k`ta4&Ee^!P?g$>pmsrg+sfky+<S+rK#WN(X$W>~+vCb|YV{gkb3b@0S!?e$mRwNww6oiFNk'
    'fa_w!w3z_g!TJUif1(s|+JBwz*k{lW`xEkx9FuUF{2BWh=m*%uci8F~zFK?kD0>Hb15c?xcba?Eu#@N6I>+gYwqd$1<f(>JCeJVG'
    '{|r6Hh*#hm(+Dwl=L}Sm1!Oi|LpGan*sU|13|kpa_QIv;C9uDv-PwlfT)9}G(jYtlcCCTEk9Bm#g-Go$BzxZdWm|G3$jj&@uQS3a'
    '_|QfJKJCtq7!e0cNH%1*z{H&``n7SWCfuHWj@9E2vHCaHd&lQTzi_|*2iS4fc3i@bD}T7Cn~XoecCu#{F<G6}MQ#4eKDL8AH@2zX'
    'a0CyyKOsM%KM#x-!2c-T5O#Zpa0E|CY_k<v=47h|7m_#m{#I?DFZM>+J!4I_2yPU1#ali!=6vXv?Eq`vfFp5T!5(bb>o{zd@$dVU'
    'll+FS{qFku(ZRmqj~S=Ny}g}1m~J7Tv)W$Z8b9}uL`^wPIO6c%6kA4yz4JOdmS<7yzQY^N7TssQ{;f4z&=-rVLCOB|m@&_=E05ix'
    'TDLnr_&&>rkgp*>G<Om9lX88tyr_g7-J=%%UvS@&e{)>RvC7vBeQk-#Bd!RZf*2XIbr;u=d~I_`xej8C9NQZ$f{xPPh~dCU;+q<?'
    '-(Qv8V;{#F<0xDjy?y2%b>Q#S);g_sIml=3H8L)+;R)fy9ykF^=Q-9mZk)KhO1{@A`=xSbv9EJKjw5d>Z0lFo<n-6Hu21;$m+;}_'
    '#d?A~@8l&}o)`Cyuco(!J^bOEqNGEfzZJQIHP<7%uLXF1jcNpVW(1!^{z>^>{d?J7i)&1(iy$}njd%syMVvy6G|qS9<|pDWJ$DDa'
    '`VMkK8@6Lf6Xer!=$Y!li=%XD3=xyaXJx_TKET#k(q$>XD6U~^Lrwrc(SFH}aQ}m4T=q9ylh+i|`<R#8H#q32$oW5q2PHZ1&wruD'
    'kn^j@x%=1GlIw)|(%16zEWZF(sq&@OWjycJxx64Nqlj^}ESE2FWdEwW_S3(!`q^qmYnFzG%)VEwJ_!B-p7b3Uy@kEhUcp14!^r7V'
    'UMMGsT>`^}Sgzsoi)ZN3YrI%dOrh%#Z^9+XMp_+}_V)D1k3SoGihNqs@jGpMV@G+Nh5ZRECOv-l5O-X{A7Gd*f@8B>M*U88xGOI5'
    'dQla_*Md5D=eK{)x^HVpOilv)Uf<h{liGXRT!C{oFG@#EvURW=A<y|p&(9skY4*rV*)`AekK+DkYZN(7=Ig5PXl4V%lVHO<XJkIK'
    'MQ+?h-qk#39F+Ksv^1u*WoJk0-m3HFc{n?-)cK08+5Hi@c6K{AS>4nOdWj{j4!|JT?POn-{j}jyZHIri`_P^Y;6|L)Lqg(+7r`;='
    'IZlZ0aH(21`fN<f_n5C6F}D}khy~@?WY0asCf&d0ecJAoFnrGIh8fq9ih5$ma_x*;71(eYg_A$B<}qT-Gh(1S&})XoWGpM2+@6Ns'
    '=o*)HRU3jmn8^2%ChjSmfk)usjT+A(RxIab7#0_G7W(`S$1mI8miAt%t@@d-S8=kMN9Xdie^N*ORiA3@oJ~vcdI#oDFSFqmYhBw$'
    'Juqk07zJzvmv|?SKjb_9?YeTEVqIs%8{iY=Nw62soYoL0c4IuplJs<B+B?W5$ZBWEFQ%Lu5mzYHs7p23;+p$>zj=BNS}N6?+@O^%'
    'VUspuUEcoyFCo5{01s2dCdMI&>*DWxkBqY%QnC%;CFLkgXOwH(hJM8F@n6IDHtXMyO(onZ@wfehykuXNKXSpuZm)^!9UW=1HALPE'
    'd=6`YwV583sK$Kc%8j~$ZA?QecxMxTf~WqHZGF%mxnfw@!a5g;(uQxCt&_W%`p)KW!K3^2YyE&dL_WR~+|7{srNAWio6P5m+WJN9'
    'D1vHOE5(TL969m&y`%TH;6Rn%yP^PId4ug8<W|Nscqf;ex?fpWlfHm>5c$u2!6zP@;hs3A92B<odM2*-^;+4;V0EeeZ`Qj$tRYja'
    'IN!$~i9;W9t#f7l-XJ<tzm9*$a$U{=LU0>!F}2ey@=@w{j<Wve%W8M0U%IXK-OK%U{Fe9hTYL^7tpzvx2^8dEz~6(#;#AS&4_;Q#'
    'W#@u;)}tI8_r3V8q{_;5|CBeMl(0@1%C1%Cjk|LcFKrp$71y0#)`&Zz#;{cB9(?5N$EDcYTSk3lOFH$`;m6d|Z|zCOSU;{oe%NjS'
    'i?LT`A9cv3`Hkzd`NW<#ySL9=7Ybsrj^E3)U)an9d+%jDi}$rX;Fr?&*zd;7*P^#&HD6)9Z6zR#y;R~BlUF-iOFt4zvlbuNg_5tI'
    '{r3VsXvO-Te9$FauJ}Q*57ysb0ypwF2|s=-FeqrsFSF*R<o|5Vi#-1JD|s@@Gm)FHI`mS~xP2j~s{Cfq5@27@nIAzXY%hp!0{lO6'
    'rF>2!ido;kEklnqLy+k^lL_Q__RI;^4Lq#kSRq5?e>WTsI*WS;dtM9NnX>ZY-rh6l`@>&F-q({UAEcg#{Dy0YQ(L0Gg?`9xaV?uU'
    'iLd#jzBZ*iUes4F^V(`CUS+~&DD;9qm1`XOVtvkd@+GZr+cBTBxPTW_eslJWA=T8j#3OQhzFyy0lkSFQtzt7Hak}%utIS?9UR%f{'
    '_HiHhW>Atzq4TnAKC|CmK>ZH3SM1ptFdgn)k<GpQ1w6`l^E9%1a?uY}27>%}4=u8togF;*ZKo!~w@UJK*<4E5Mjrc3C4VZ*?XKUH'
    'Z2zznfkp6{Ma*i$>r9@IH~-DMd*yNiceXos?^VXaYW>p8e|yzY{`|6^XE=Cr2V5tG?gHi8gw?ICe#v5msbak{ujPjozsmM6=XHM3'
    'GA;tM4c^z!b#j$^PyPYFTW9)U9D>gcmGm~a@#%<Sg`UE<^EH2NKO680X%ggkb(Q7ijmw2&6}V68aeF9ZS|01Lewt5eOdP~PH$9&m'
    'sm0^Ujqb>X^6!*^?IZRRMu)@&Y;e`rpUb0k?N8U!xnA31IJq?K=%e*PetAAx#r?LtUYgeRvm5yrpLZ^KKE&;U^epKCa!fX>m*FUE'
    'Whi)q>D5*`=M#&Mc?=$W5hLb^*-?RSdq<RixZwE90o4<|+xXz)*@>0=J&)s&NAo7_*2XiCJDDncwQ;J(bDmpy@NqBUvHb>Xo;gnX'
    ';JZ|ttUr@nUMRP!@SA(HFYsA&xU*(L7Mp6pgg<jgvDJ+QKl7jRZwhXKoGzb{{AYo=p-|apDJC;pFr}UVe$>eJe;*Uu-FuiATgbP@'
    'QdfSJ_V4cZHlTb;2S=7E2bHgLlH684iT^ckF!Zy}IH&19oDI6Q`&N11uw6g5^B3e^`JCX(^_j8_zW}c+#Rsxe|IIaZnsZ%Q<bMy='
    'tK5svGx)aI{L7u^v8sH(=!tk7>;}2cG`bhFKEt2*nkQeCO^@4o^Q3fv1=s^&;b&w7yF7s(eQIslwO`g-#-S^7t)E$2DFz0=!acvR'
    '#+MS`dX!7>^#aonV@3S^`KR22`&pJlxL>!o3Co49_bYLfJohg0mY|j8|D0do8Eb2^E;w&~9n}PZW7NCMb1jMi_wuakJX-lTA-n$D'
    '%b<DhH_@x12gt7_#D&gGpV~^-(`SomZ-MyacIr>dj#A;`ch|M%J)8VHmdAzlC%4m>d;MN)2SSDGQh$bW@ytF~GsF<c`Um2@?*tsv'
    '^H^7oc@Oq*u+6DYGs5t3!jFW_(@QLlfa_OzHen_8%HaPrb1vZeC*%Tx3;$!i_+ZHIF}tuok$;h{=sqcOLMdNgn{<)K$3E*LpUKAA'
    'y%C$-+#cXB3|C_6Px0$$w*6<np?Grjmpl2Yk=^T|9ToCnvzTt1VPN+6M%FtMWTnaz-*M}!-IA`FG@Ibx;i=3{s(kmR<`oDvnz!Tm'
    'G^-`NyEoGf|ND{GK6tJM8w!@JZny&X<@4aBz3^B~x}Kj;SjW4yxl+q_s=wiVQ|UtZzoB~U8#r9~`MfWuJy8s`rRnx<(ApzjP~Vm6'
    'T>-bD_5P|mh3-K$7;xqK$GnYUC@}wlUg2-=a+j+O>C^{plx=7fN5EGht#H6A-}c?j6j({KX7BaN>%DjKj_jF);n`k~Uf&lSV|c`G'
    '_a@C8w=4E~lWVXUsML*Bo`+}a9&M&u&kzD&@(!FDes?ChQH^C!cz^XzdLBP_!@s|rGQ5F(UHsS0I=I8@A9Lc$+E(dHbxp8`3-bqt'
    'UFrMWiP=%7gfTO+N1FAG@|=p<pWC_j+am7dzdZv>YK|b|_d0B2a+~9p^>@CjH)%*U)>;Mk?%bE#Wb>hZZ+P=<9#YuOU3(;-B%8dE'
    '^E-P-48HQ=a&AF-0<R7-JF3(dYIz;-<9G@V44kRdNC*QS@@%Yi9zRiUy#_8w_LS!py9&qO@U?t}|IvN3vu1Q2X03E}k)4lfKdq**'
    'p5k{R)!7RUFhCA7_}p`lL(-X;>@(v3!q`cwv29YhrpTdIi1D>b4QkOi-LKW%oNK$TuUxmI*nX`)4XU>Fk=&~`*m}4A%<u90I?ZhC'
    'kUNTqzY@(PdVO5O_5#c(a)Z@T=}lQ)O`L-IZ#2K>#<i6rv3P`BRJob|DEnutQpdbm--7OEvz&ba&ho_0Gug3qsOUJaZz9jdei%n!'
    '*gTjb&sSGGPi-|2_l~!6y61b4@A;z|apC{(^Up8JpXIA};?J-K+qphxGo@Llh&a8{_Y>Q&c<wl0_`hKsBi%9kF~zF=@S4DtU%!~V'
    '9(#{Z6UKu_vO2!fw|5Tdaig*`gzx2++41DIzSq6S4+F1XUsd-fz{h&~n{#t477eM-ZD^63?kah^DQZ6B4)D=zUyL^ct7JAq7B+gX'
    ';0O+IS?Oi>NSd*du7vS?{Z~1E`nYy;K9SCgT&rD@U%@#`zsqu*D!#U=`O@SQxzFRe>jNHI=^X}n?v~ZP_tZ0doxi(|^GCv&Qr*OD'
    '-?Kx#VH-p68_F-_{&XF6W{aMx^t|3A(uR6>QR(Yk^OW0J(Q=+r>S^4cGlRXYl0x>tw#f#35OzxaVpnYV?m*i*G-D=O99OdYOhs9Q'
    'pB){8<sB!;xspHEw{6?a@y<|JtY2#gKK9PeQ@Y8S&N-Zsi|kmA1fQ6TTFnuM5#nPqZl71|oMcd6=^PvBKjcdkx2Dl6e`awnHUrn!'
    'PHvyLDf^Dq(A=!P?I!ir4E(_E%k(|<`d6MwGYM1dwI_IenaKqFaPJIg{;x~DpOpNT&C?=A!_N^jeBX<yHs@on9>o&G^A_}|o#;%m'
    'XEg9VbPBrwmphj6jpRGe`Xovp9G+okk1%%wY>em(D2ofwfivTM6_?Jo4vM-U$$Urkemr+gv#FW<YrvyD;sxSEQIDkkgi988r_dpE'
    '+S6zAc8li^1C{6dbjEQ2nM>rqnH>4NVeGM*JDU%uxI>?@c?8JeoavWvx;8Qd@?q-T;eK=m7MP4!z;)7yEKyHgcE;|~$nKrVU5>MV'
    '=XFq$WkRxaV?47fBVVlN@r-8XLs}QbI`9cPBd}*S5l>b{4W)g<Yl3P&lydxQ-Ez1E=AGSidm4%5erwkAj=hr?fMd3ws=n0cKH!OZ'
    '!0Z}4*qYZ@=O1pRR<s;|pA6LRqeT8u_6^Rz8XHHlj&6T-qJL8^?rhWp*%de_eBg=K87TiU{t8yZD24BBp<9}JWpRR?!|%}f^(;=s'
    'e$5-S(sA%~T9#`Jyq0ma;j^PnYdaEIKijvY$-y(#6V*canF}q~J=;IS@SxK^B+Xxt8Da&S_viL9+W7Pif^YN6{6&Td9VWjUJu#kN'
    '?nkhm%!tj5L`RF}k%LCL?vdF$VeQpUl>y~FSKXNs^W`Je*_Pz1eK{G$8qNRKKAH1YeEMDwhu82LCoA4j+<9X-Qq3KoJen_m)Gy=n'
    '{=xhBNx4Id<?=iqez&jpc}?fCU(PEwPjY4V7;T8tu$sd+%0rpVX4U!v=_Q+!DPO~SLuS@1%xlRchwOXAz-fk4RF@_jYRwCs^l9I~'
    'd;@tCn`NDR=XxT0s2xk6L*7D#v+{ROfY0-L9Lm?)z)G9)n&7Jc8{SFv3N{1(5}r>^fBo$qM}3#$!9Jm{Qhs-V{aGLMJ9%I5wpIn%'
    'm+QEB9Lr|oAMjdW2{<*dPkSrd7@x_Y_at2LhV?~0x}Md)8WY$7@(gghl=R!U<xXYWNnNUiN8GmP{&(#BNc9bxg`t`f@q`E0(LS-~'
    'UJdwtbT;~d+bqQ=R)^rvdS~-gZ)_k2O+U4NC)Vp;PcGv|QFD1&(|xM%>9~`RkZv<wJjj>WtPbUr*M9UBBQhLnw;FU#y)=i<;*?wM'
    'w;ylwpK5%n^wmmSRrxl_a=l`Hl=sv4+$iC8SgOt3;ohI(*<bC4e$WrNGl%&hhkic`cheVWKdg_JYy7RrTGn;swzKYHHK|1lqg=D1'
    '*{q-RNUvwz%Y6IYyd9edquFTqJmTn(`*x=mjOJa~9hcF~OxG><zF$u+&-87ki36ON@Y;MreCgU7rZZo3u8}yH4H?%~x){;BZrE(%'
    'sNIqv|Lt`ym)>0?L;lPs_XWSA9A5MzssUK04Ve;lLH<GO#qHDFZg)jz?upZT{U>l_vcEcEIe0AN>QP=JDBHdjBVU*mJ;}&T?#}~Z'
    'ot&HFK2#UW&q7mQVwBl*G28ZVF6Md$(U!oM%k|z4%|A_PU+GJDNr7E-F20fXboe`l5KqjkAJ+GnjGb8E@A#33bAz*Ns<DH(eYLN{'
    '^A$GNYPL=e=cYy7>CyXgMr{_qSne{9b*kTk_eH70{d;DUzTkUBKGth(m&6wa6i*<d0N0qj)@3EF7M*jN$4|(2SIKzpu59pit0Z@<'
    'C(Zfnm3!uT<ex9$A1oh2{sZiWtq=|^@_%P?%I`t%!O(UNKSO(j{`OvVUMwYCq?{n*Ga>9QVRge2pK+7=yE-n(_yNC$4R~j8zx^m~'
    'z*lAVP9TqF*Atn}Z&Ob{9Z5r9ov#}jKC|?vx*Dz}Gwn7Ym;4=BG!I4Z#wyQWgf#n3?+JK^t6A;0u%}8LE6Yz(@TcNDe|1Kn$X!?+'
    'bePSIH>jU@waZl{9-m(#Z%6N*0#@!2CytgOkS}SL;o^FY`s?6omwZmNP3NwV)1K%*rH4FEWVqqOUx_EvJEKS^esx_uSH^Es2l0$_'
    'ldX3Sj1!QzZs6Pg4W8|hU#?$`-Vd5rb;a&YpOf#^E9`1>o71c&M&rn4g*F=b7rk2wHcIcbD(7Ckqr={{f|x|PFY;L4Co1O3@$YNx'
    'nc*k&?jSe5iM3pw;r;vxdFRn9<0riXCXuD3aoCM&m3;><5!EU4y^*a%A@y-eSi(5RZLA-O#k&wbfloei0^~gTTnLk4v~@&z{RMl;'
    'dpH5ZdA8n$Pjw56`qS`NC+2aU#Rr}XavSL*cW2j9e4$*{`$6*c$QNg2Zo_qw%fdDWT+cn~6E=3PxY{e--ht{Eu*rN5N+KIr!j_eO'
    'u}|nfs=?;AbPgMwslnn&#ywblf#QNl>mhui`PKvLZ{+9BS&d12qP3hTmcYJ?^<ke>Ly0|lE~}$MS25Kvw7hOmiJ!c#p{HfJGZ}Sz'
    '0%8~Ccgd*Tyo~2-iOzZ4!w=wo%6u?;KOcTe^OR!;{x<F?z@;x?UgQJ~W{-%=;2vGX&EaMwk-pcbs_$t^A;YjSBd(I^_MUA223z$a'
    'N2K$gt?euEtpfk5y?5mJ)pyB}d{{4mxX6^|=u2_(Rv(ljBX)ItI_rSvMjV5>5$x5)p8|Z8>I9j;bca5$Ng`|lW}e7Sc<gJiGidaV'
    'C&u5H&GvHqq}V}cK-j<ecU=~HHN=ils0#etEvw-nC%&9$mLBUaxJq@uk7`f)akMG>Y2)O^?up^gOs>kPR+8<kh*$YJfE~j_QD>Ov'
    '_Wj1+5VJb4Rmy3iU&R^xd%@-}y3ugPdNBNcS5Dep*#q!2%4gswh&2U=ozmIsEWaeaIcGIkrW;=wfR_*0`Lr|Pi6a)Z(`V0UMBG0c'
    '#NQ6czY}mH>T#uckITZfgxgeOCI56bMV-}W+yr<=_02K8mlErs_fr;J1<$saje`F`pR5l;F_ikFtOoVRe7VrajV~8+z3prM4K~oW'
    'OosXXE6rSgz=8F5oOH2T@b@B8Ob&tPE%I&bkMnK%95$<_BuC^1@Im-8$AOzOFchQ6_huV?|2k`?>MZLKWO)bgX={6rau4`Bd;g`_'
    'Yq&}CQs1`c<Jpy4yL}lL+zU&yxS=Bo^d1zdxe}*>t+Tuu7{jr_GM>P3rr;9vK7!(R3;5#hOa3mkQmaz`rMyq0dRdtDWlruu+gOPl'
    'l;nP*v)fu{ana_@vr1f5)T2!IlSQptl3ym*_jT2*-&W|jbgtrx?=OR^eit-DZ(Q;@U>4```$LXFh?hU%t9*UL&4Jx#ItK|ZP@{d)'
    '9H=F!tBJ|ZA0<3D%5a_fPt|9i?4X&b^X7isS?9UKZTvWLdEmN^Lj54{L3)2jwTE>5yp`3D^ZpU*`B0vEcBB?~ZZ;Rt2ZxiWH~uA`'
    'K7#|7Ywj#hrCKF;53eo24s209mF<3%cI#?qBB=AlS?x3fnlGn!KakBXdRnW<vls`w+IX=>Q~ev_H}woWfz>6`597C4!mJhL{LY5g'
    'eIZ+A$=>;Z95F6@rGq>N_oezR#aO{#GVV@i^oZM+o}1@J?{km^z9;|NAb#|4J<DbD`WMLwc!}6?J`iTGyjjv&&HoSa|8QPB1N<<@'
    '<bGE3=~rd>yZ$((K4UB&e!{C3jDIptt?lg+E|&N->vbxFtcFDMtS04uLdJ7>{Pn(w=iDyw98m*i4%wUt@59Qp4(iLo&OG1E^TEN;'
    'r*|GN^FCiWHzXO*jHkr)kNDkVIf^JyZ3A501J9@WF?=s(voJL0!)Lf8eNXk#S3}3Y^IoS$c_{Jm<DayLLPxU-Mn~D&D|rlG7t3>s'
    'y2#%UuNQ<1uEftTm$92_r1%ao7k(&BA-~1P@w}P?mGuhyAUmhMHcIErhu~yhM19*TZ#l0fagUv|wzFFJbO2rk9oocMsHQY4{P+61'
    '<8yOeyK;G&N%8uNJU3)@9(o5X<^B15wO6WLK{koYYo%0sW4NMpl(RZ#`6@fVPw&HU63(4VedMf$M6(P2$)oqJ^yyu9ye7fkg&^u@'
    'iqG&D@R9mz0{sH}=)5h>sn*zeo}3dBHt|{w&y_`1w`KKKI<rhYDe#xTHi&n!ce+tO;rz$)2!ZN7jWj!7&*NN`PuA|((6wjq`!+gu'
    'fFt}}l&uIpzPG=IY3%)MR7bWA`OMyfhxqD<+K!z+%X5p{bJRRPD9xp0dZ71f#59-4>Z{P3M|_0OOY(COxvk__%D$Tz^zN#bY8mwG'
    '%%8hEI)kwV&!N6wjq2hI2YQtpiOn%^TeSsx4*~BJ7k;{4nuzHGo$7PIBdSl(`6m4j=9b8P*xZW#hM0bGX-1fxpIhX$qU?L(&)N5k'
    'uT4J7Ig0bVU#a0!OyaS%93L~jGrv7gEl_PTvC;|`6I?b=J>eK`2=6dF<1pYMGWC?fGvpAQEg01rktbB;WY(xg<VVO^p_|6P-M(AQ'
    'b5DVBbPlgH+j68{!c8r-!*WN1eDM79S?|t;VjXgW?EK`qYSR<qlUP5U=|GH}u$kzj6#!3E_I{my1NZh)iuYva5BMs}e+a`fdpX>('
    'mp=94#_P|?B&!Kz_i1(V`}4Vy$LoL%6W)k?rb?jqhwyw@q*}Iqbjb(AVPlj|jw+kY(K^WYY^8&L^PH#j4xgyN0?x;1PJGIIsPZn*'
    'u!3V5w^)?9^83$j=l)B4!856D+FL)AWzHkSVvi?#CP(T_F6G*+hyPZ!okcPc<gv}p!)R}FQ42HPO>#d|e>AtnIh%i>`8|(e75CwC'
    'Ui^M;PYL+CDc^-ZLVml(yE8Ktxs_@IYzC*fvNmhjr0?6t<uvYC`$scMS6}0`52`KS);^}x`<(B7B9qHo-YYX}h^1n*CcX&YLVn%Y'
    '0K?4E{V7iK=W;&&czx24YCJoS>e{()aLhoQU^yi9mjdb+TeGLyC~UG>s!7sn8#7@(nKkJ%hK=LWdxwcTcr^3XXEi%^u7UNtfOj^{'
    '-QJ!h?{HhCckPzuWXop`Ze~jF^v}(FeopzO_w_pCH$30ly~eDD&T4A6J>;*|tK3s|ZV7Vt&o2@`XY#VB;1xf|D<U7Db5Zkds-+Wg'
    '+*u@As0Nif;_GuW20yy(BNb;f7>*FmHNO`75;>c_X`GjX=0CG@H*)nk{48y8p4TY)62VQalfAE)YMma<q-8VQ;0gRayTPNiX;f#f'
    'QNOF?2W)-R8-V?$;D#so(!mwGC#_vSkEr)wQ&*E{eV}>|ea2+~ev$Xd&0S<)XH9TF<jOJ45Yju0uJ7LFv#i>d>JG$DW_gUw=35CX'
    'mdKxg9W=+0&|VooCXOAKa;KlqVn007!_Gxgj+FI7@^@dBXLKpACcJ`8^15c9&JZ@%yaxNeXH(+f<@Yz0=S2&S&ECbzIbOaW=uQBC'
    'h3{?d{C{><|N7TI{^x%I>N_aF'
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
        print('City Information layout and contrast fix already present. No files changed.')
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
    backup = backup_parent / ('EK_code_backup_city_contrast_' + datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
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
    print('This fixes the City Information search layout and improves text contrast.')
    print('This updates only the City Information template; no database, media, migrations or other code changes.')
    print('Stop the Django server first. A backup of replaced files will be created in your user folder.')
    answer = input('Type FIX CITY CONTRAST to continue, or press Enter to cancel: ').strip()
    if answer != 'FIX CITY CONTRAST':
        print('Cancelled. No files changed.')
        return
    try:
        apply(Path.cwd(), Path.home())
    except Exception as exc:
        print('STOPPED:', exc)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
