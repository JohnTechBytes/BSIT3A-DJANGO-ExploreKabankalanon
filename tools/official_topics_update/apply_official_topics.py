#!/usr/bin/env python3
"""Install topic filters for the official city index without changing data."""
import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import tempfile
from datetime import datetime
import zlib

FILES = {'apps/info/official_index.py': (('e3ff144d4f9c237b20cf7b8cfc3c0d2b1c7ec2ab02b2476cff2a70f419e8f0c5',),
                                 'e2f18651fe3e7eda38b08f6b5cfa0640f2183134e96ab2f10043462c43fb0154'),
 'apps/info/views.py': (('edc43a277bc463f0e0b7729db9ec067135fc8a8c5ef52b4c6d08e1ca5c11708a',),
                        '72f1bddb4a8147ba94c22f65fe23d17082a9f49c8dc602f42279eb07c3c8aba0'),
 'templates/info/city_information.html': (('3b47226fa750eaa88968caa00fa31962196ec8054d79a527a530ef37114b1b87',
                                           'b684c5eac18e9636ed767662ddf93c67b10b0bdce2b45d20053dcd35982596bd'),
                                          '210bcee3c9da824a502f8a2d5c4f4a1073d9fd52b5af70408b27c5c866979704')}

PREREQUISITES = {'apps/info/data/official_sitemap_snapshot.json': 'b2ea5ec19f1bcb735fcbf655478fb5bed288d3e3366c15719197d58c1b9a073c'}

PAYLOAD = json.loads(zlib.decompress(base64.b85decode(
    'c-qZ<S(D<(lJ0-$*B+aLM5-zovw2`gBulbMpqDWuWr{@tPO*xy``@pB9w8|NWL9N$_qF>_Rtac{@bKmHB|QH3kNIx5|JQQ!zWvu}'
    '`F7s_=Pv%^zy2_n=5o@qmTog#b*h!vu^a1-T{^n0buiGw!rQ3Qb|dHHMcTq|h9`Gf+4y$2cBb9HiAu3qKP+ZZ<2ctF`<eZ8tOmQW'
    '-)uzAva+Jjfma;v+~zrO?Z$Ct`=Qxv?A>amHlGd+vmPGt4En7wr+1pIb~w{ZvD4}XbGp}WE^z(YwZr3l+ADYwT{m^Y>ZY=ABWvGT'
    'Rwnaicr{y<g`-abhyM1Om&F^6&DD)Pjs5J~?LFPQb?iYfn-1}em7E7XV-Ps>Ja;oVIgxdx@Aa8|4xFO3bDGw*f8Oo<YGv)}*41np'
    'C;aW$m(Xuc_Lzs?v|^&!$y-)5cT>@3(Pii9LEuH!$}P6nUi|a|`c@++cJ)HwPuqK<^Rh$Z_clG6TX^uArI?<pdC?_wqu$ABPF|Ah'
    'o#u|l=$|_Dy%$Z6UbC^8+Xk%z(LK9&Ky=-?L>sqgzBrrq$sJYJb6OKee?B@*^XS?ojQgtGQ*(>f(XXC^$zT_GQR!edhyR}0#>S0}'
    '>m1iKdz#Pdpq*(h1+0x54MQ*3%6F8HuI@y0ySJO!mv<T$@kEeaUq7_R>*1K_GZ|}@_CV|I%~mg*P1~z^qeL_x#&g@c62HjzH_l$G'
    'dz=x^;rmW>InDF~&C64sd3hZa4vk@>R2x}CXR1{?^!&Z6_kK9`@E!NQ4L*9FMzpo|UR>F^Q(CjlK=AiKna=|{flo)a5z+e(#6LS%'
    'e|n)Y53EVMJDT*~twuN)THWAvRNnIQCV8IjtoifgZCVLC>&C=tv?~K`*d7<2_GZ1e^IPGKd>Q=NYK3QKWHhX`)wil^ypzT@3wVxJ'
    'X_voe5j)d{=8%lMjJGdlwH%mL;=Hi8b&Fo$3HhdVwbn$Jg5PQ{W<{P$Kx<ClS-N8z1+(dEbDP#UCV4GZc>J`skfST<g?OefLZ@0;'
    '(&vIRT@*UR+h(v0@ID^bs9Z9eyl$b>D6K%dm+G3HWlCLQoMzE3q<7PLI6JpR?^-U-^Q+b!7kZuHWcWTPgcI8;4My>r=oZFakrrqm'
    '-hnZCQAp#X_dKTEgXag59{5+`F}>QjcTF-JUZ=%GZfR~cZQ^aLka&veJ1q_kuW7wc_3-#=Rjk4KLVR4J@l_g=_$;5hCjOM`GOC0w'
    '@%YcjW}Mt;f_cejbc3;ep>?>>dk>_~h9~;Bb%@Ts{tSImn2`>I4)ehmq~8*~>XW{l$4|kyNY_uzK=7Uw)BQB|39oN;$@5>4jPIbE'
    'pg*7+NfsA$Ev;pnc)k(S`*x0Q(3pu&h)1A*Nw*c|%?9aa@RHB+$a)$2z%J>mSM}17bRp@JCo!MqC3N)0iukkuzBg-y;DxUDrdCMn'
    'c^nq3Nhk6{zZxugJ|lByLZ=bWzKo13@#oGXh8N?eF)b^5$M%V5!*_9g<>(d%Y$GNOt2(ZSwW&6ACUtAvm;CtAIEZ7#7&BdT@rho{'
    'yVXpNI%}VvY;2tAU~6vbG%o1*GI9L+NVJdV)AIJk+JEbg%jc=&Pfxd`ZTak3y->>D<7diefv2+PW%GTh(z>*U@yzZCo4Gs(W+dg8'
    '|86Wvw<mv-tu^;%wN3WT*%6N}=<_Z|BjUXY)<(BtKbnx;BtEPOdcBS+d(!JaNM}l0x!5t^fd_2kO6z{c`qRA&FCrT|?S3b^7KpB-'
    'ON`Jz=ilQ;q=TkI;x!s~UDZRz^^V_~+U~7MJdbx1pQp6g&~ut4q9ybDQS$aZ{cqQv`72mLpP5VMsYIu}Ghc4j0d&7JDlhXm!Q7?t'
    '(_ooA`4MOphCbO6q7C5&=z6km0wbKo{7X@yPg7p2J_RGpKmA-`yOPk%OXx*&#x-Q`V;YOZOj?S&5_;1$C%hA~=oPI!?DcF~Ib&X='
    '+m4=2*N;HYNieY6Cx1E!#JCeV4I>_lv<0u@LdHL<t*STgXhrre)%`RclFwcNHdx3f(O-G)4KMHL-<|zTXiv|SW9yxK=zHk;)?OV;'
    'OnS&QBetvZeQm$Ll;3ZLCt8oa85Y!gBG@3p1x3)sgsvhTL$o~lBqJpMSCT75=TD%Ai02JFtKf_lgsp}Px28$l6fEcVfUa3fT~f%?'
    'Q`IZu934~K16`EaGlOu{h4iqwRr#6!HR@ZUTfr4}XhpKZw!ph;w`;O9TZHFE3*wR9ik^FBdWR*#W<8Rd;eurO`Z~SUduwHUWmV^1'
    'fpuvOVar*D^13ypA@M>sFU78_^eo-;2w@uWt{g^ZodX=BtP!v@*{Ju~X1&d?yU=YOaOsl&KF?!wm*`N5dsb7OY!}f^j@5l>ISaSN'
    'cAk6|vSVb!*_XNdo_X~V20Zd-jps%fb8#XXhrpIZH}WAa8f@u3pZ9z@=MC|q<^hipAJ|&LKMs5em2RX{F63WXd*<7gz$!D1uvN1}'
    '`kZ`}+?s?$UyXUo)|q~Wd?v5Yn;27$-jGe^!_E3Q=Q*XevV?c0w6=2cgn91B<{!MP%HQIjQ-rRm5LPr6UW?ux4YqG_TReBQ4b=B^'
    's%2WE#?rCROOjzpci1jD7hF#|(4F>5DPAJoO4x8Uw;OxHZ|wWgy7oynLP_7u-Ze@;;G5)ZfA0R_$s-=gV*~Por^Lra>pIodYpvL='
    '!nPRUTWk2P`akgP^6z-0TeD}~=+}qi{RlJ736DC}&oEOt#Sl3kjql5_#HbMVhmG#HJDsD_hkdX?PTzk<!w+#@vvejK`6=c}>GtT^'
    '!nT5c6MypaaX(sDL2Jk`$&b*%i7lP#slM5!-xY!1+D7NW`rLd+_Mx(y#i}kP9ANw5R5vu2c-jLd`G7X?>xC{eFGQDHIpg)>Yb?Uq'
    'wzdTBA^BZ+dT%!$1%eL}?2&t?L4M6Jq%j_5_IWF44=nw(y?NfwtUU$&@x3hHT*rLS9ho2TF25giohY%2mnM85#)l*$rbhe<{Pr&9'
    'y|@{3Vi%+?X<Ctp?^y4o%a8MTk&Zc!V<pYu(+EBPUB%jc;<-!~&P(VWN%wC=JMr#K;cosCyX5%c{=F%!2$ySDJ8oYHe_#x^Hu~Z7'
    '?_{)gzYbC_(Ks3hPuoi!(Dp&=yZg&`bO9gT^Xv8J?@8o#%D(-*eBH?)@wne2JxTO_jm_XC&c(L235_z}_u=@MCpyt$;c2Ba`J+1d'
    'I+_;;57#{XT`Q^2p!c4!29m$vTkp3jt;G5p>isvo80<dRO>BFP<gbvOfK8xDJ&++cvY!0LZ;kDUIE#1>@&Cp;5Eh7Es_R`f!QPQo'
    'Alq|H<8w+Z2t3ZVHWslM#4&QQsfchb%R=RQZXHQ(2yYTzx7LK65G#Rg=4W(rywy%|jG{krZTkJq^#X@jrIo<ZkUip!<wC_IyPJCi'
    '_HHQmw0fF5T8Pgr6~nLZ?ghpW^gS?^u+Mk=LwZ7B{(g$xfIlSeqI)Dh0lrkmo%kohuNPw=yjCmkKzH`frw-#C`5R+^I~+W{*EyeH'
    'Q9&oW_nu--bv}*4{=;=FrgOZ*^*1zAf4@3OoPp+%`EX}-%*$K-D6h@i(EK~@Z3gIk$N%~F++!K6!yQ)1(;#|)32xpcb=*(y^J02m'
    'WB59$hqXy;2>eSr>1J-9=_Anpv)^yV@Bz-m_#f*Od4C01`M>}84<+ZbeScqi%X#=e%Z>kbQIbEAwQ#E1$&D@s1OBG<#K8*@fK&oU'
    '6$Ed>cCj1y<V1Q)?Mfj3Ohy?&Vab>XPB3s^AoxyrbONA7&mm@*1eVqAa&S2+6(B%FR5(p1XDNadS>gnriMS*zend{?vNC2Tz;2w)'
    'rWOig-P;m)B!EyNA=n9!)FQ`&-s3kH3j#w68Bpc%F_Ur7vav%DX*PApA%>7&AY|lNYcv<D;0TbkB0|S-j5@&<VeXeS3DMkLkpxf^'
    'Bh@HN<hT)>bP}FsqcBU85e|LdE4X?omw<3vZH*M{0)h1;>Ej`oMB|<<v+E}Kt}LGg<I2Aq06SN9H05=qkjSYo6`;VtC|(iH^x&l$'
    '_WA>>G9J}S6A8`=^XlS#s*{t0z(P!5oapT87u_L1$qA|mimrSztNxk*^P(N|-zvjhlQo$Zd&k+dg2Yjw6ES@@)wM_f;eBth&-8C!'
    'w?SKDqq!j^xgnZe{i^qko;z@hy+WIKqfPW6!P*dQ4ZgmReMXR)Xtkp?-n;`q#7F>6RGuS#cux6C1U;St1lLG__C%`{0%{I|<_N+t'
    'aHh3sp4A|BU?C7mP9@z(4rP~v?2hU<z!`5?qcH={;Wp!G#ldU#_Oog4I=4YDVQ{_cK5(bR)6I~04SWj4)1&8Ui?_jcWlErIHtQ@a'
    'G+#Ju3zrj&oE+T{e_hESU@liO5E~IZL=x13?8auj1lb|S@EQEDBI9)>`j7%4V@&cWoTt*rnp_%_TyV`NLu-*k);oaiFY0Hk3n@Y3'
    'sU0~lymn+5kfadb=>`67#z9CcMiLccApXeKniRHgUrtW!ks<Xprxh;ddgCb8+zAm_hM~Ou?1}3M)bzmP;#uHTl0ErbgrKhcI~N=m'
    '&&mgy+wnS4vYS~1FluZ-KRM?mI}nk-cpLHavd`15n4?JakP<H;Xcx+Nh@ff9x{A*nD5vqR)qCI!$oVm-3g)fw;4b++I?-84$Z2#x'
    'f9CrkV>G|i(6o!Be>V;XfaJIV&USAkv!q{$M;kGc)8bu%Cmk^#DZg@@>T|@nL!u?=2EKMnGI_=tx>dObwvTzmv#BZNmvoUGCUVR2'
    'HcR-U8O8t)EXVx&?lco~4M|_^-C}rvepT0lboq*$JAlMwUI^|XxqX~TK7xIKV@dinRC$ABAzSkz5*nqwKTXyg@3)?4JQ|Yxtm7Fh'
    'i}AbxBu&9@lRyR=<vp-9CGg1Fw*`+AEsykB%J}d^JkRq;c+p3K0f{!fM|13vQ5NF{54xKkbT*tJL!GzOy_!sLY{*&N=I8K~@x5~0'
    'OA3%wI$2+#-GjM{wI#=cK%gZ+Ea^$;7I_cNSEFZ>ZfaSF+&sws(mk~9Si^yshfYp`;2&~EhLW!IU6T_@{4V0LrT88Jckn7>f`zX)'
    'VtFsw_aX5q5>zwN%RbpB`K)4v>?Y`J-SHFY%LD1#BODh=6LP40d7pKLjdl{bwv8jeJ<(4-hvh*AFp-GjaR4VANUuVErECMxw__O?'
    '<~4aABzjf^B9iftzNc}9S9ioVZ<6R&splg&ZA5PZ{xqgU*7f#+X{|R5qCf7dDmqE(3!zUyf8x(QWIbIIPV8~;8|$$dB)VwY)@9I|'
    'lY0_mGGBZokL>~%@2Hq?4cfalJ7U?GZ{?5e{+&#I$h++V_)W+e2aQtxlVi251Mw>T4P25w2Ra$JE#&bCTu}wjC3ckgDMwq<8@2|_'
    'Ml|8;``{0GeSWRedxU+J<NVOpVqCx|Rnjveh}S-lZiS9sCkco&Sda!yZt&yCQ0|*-+XbUJDu7=TM|Dj!Ymi-WPHvM6C6f1v08g>^'
    '4rdYp1iu+<8CzD@-?D@zXg>&M<gA01A{j;3MkSKjN`Yhw#S6syXW^8RZ!iPyMPj1b<|LSsXj}jTF+E!R+_bo120j%wQ&}I8KoCV-'
    '6Nz_7-mu0f1ha>P_u8R@A~JgB3;~9!wg&ES5Ll1_5MLIIy^hKov+5z>6gvor+ve6=`tG#hzfVVdmQ@qFq-k(b2Kg=D9D9(^gfK4('
    '%)&DYR$gMhRtEBA@KPkF3gq+bMM4k(Uy)c$97wZO*^;bYk!S+$wCbe+l0TEs>JF{$Q6w_D`GEKBKMpcAj&GwNna_DnwgY%nj!P8B'
    '$$5)lfqbt_@QCZJYnGr)`76P&Ync!yo4|>5q7N4tl~tbvf!nuM54>0E(z8S`w#Vy6c>g_1U}k|i!M6w&vLA4Co23Pfb2}**l}V##'
    'j<o@NjRk@a2yP+KM|v7|Y4bYr$+pc7{i?TnSoG64BndP@ck*#a7LtHG@OELUqtHvpph)%(Y5f{*I}1>4run2SC+tO{nP}AN!KW>}'
    ';P2{PFkW7Z;)ezC@gy+E1=tC~m=)4#>^mmckgXZ+UA-%>Q41vv5loBxlTUse;VmwbLU0rTtt82=e&=l3gr(W8^7p@-%pqPN8xxuh'
    'p>u}h*V6slwq_x?coxB^ff5ioXZ}<*NgR5)#1i>k6;sG4`_HN`grX{$j5s>5C&eE03W~_s$IooaU;|kvT(04rBFR0;7j&>}^12-7'
    'Qtsi4qJS!uVUm;a+UX2npXoZH9bpI&Xl7d8$+vfE=MyzDz=rp*o&<jq4>VSIc877Z7qo?soPIxzAAjGG-*-q>WwI-=xg=}k*F?ra'
    '6x%Jx_E^F%K0i#XA4M^TLH1(50k6a62%aY_CxVh2HEG%w0Wf?gWTO0uo)P~x%twuqd<NM-S-5HQvxdI#KOmpZj`&2p??%pk<voe7'
    '%X5%_Pj%<yg(c>j7eV{ouRJRWF5+3P2x#x;(_QFP7s*=w5NkvKvmA$|v?w4Am=86tc?p$50|eC*9d}o#`qE01fr-A6NtD8dctFY>'
    '3M1PGPRiuRC5tVxMD5*p8iyoF&$>+}<yp2<c~r+!eVj~s5wa(e$Q<7gg#dQ!^LK5nz=3F?KklEwc(S@+y&~;epx8Jbj~H9%w$s3<'
    '@88=rfz{-A1YIy56o*8Go9842QS=<E@bbrh{Bd}TcH#W+CZm_$@(}+I{`wKk56kW5KNp86{Num=c#9_}ODjN1NP{m?LPlEol$Cz4'
    '<vh+?!-HEjgZ8xWf_vC1RnyX~^!pi?9q$uuMBi(VOVztCMYC=_5eK1MvO`=)vptYTBFl|2(Rh+)-9DSp)|yiwK#OrXe4oOiP7Y)_'
    '<9RI8EGYMko)01nUJ2*1wk9pUVhyrcALKmgJ^RBPsTPEaM;b>>o#{Trsyod#mqwdat5n_KJNdcQ`!Of$Ez+s<{_$mzM5|s$?W<GO'
    'uEZT@a|u*oMXw`s#Zl9x#^pz>y;jDUuR*D*h_peYKX>%{pFf@dhLQVw7I6a&Fg`;3<lQ<%cXLCigsenID=pdksTy0qsqM{Wa_uMc'
    'YZ4kR5|@R^y>!py_tuKm{Der#w1`L+qRGq?xo3!S-}T<C8zD+x$f~{0^d7bl98rq)({~X6(m3A<t&>J<L_T{IR_T?a*L!G)J=Vo<'
    'k!Qy#GL&~FYt#PT9w~gR_lT!NWVT}i(eICVZX4@7GJm=@*!D2D{o}OQGd!Z9J7WIeGEk15*9uGe-f(eU(+Yi(DMFi}vnnj{9Qq9&'
    '!wR0VSL~jEFkE<VBLkl|Jg?%c)LoV1-l~4-)@FyfeIc(<Ztp;pG%j3-zc4SPG)az2E9TR|4&TYoGId()72fPi$Z|B;K8vwU{)9GW'
    'IU5-d<f(jw+=!^0mZrF9-M(|=rU(nS{^k&}d8>g3=>Mu#r172m8=pM=GF|5{yxR83YX#roA$XC$b64BA*Qz|3wQ|tCw$Hft9a^zT'
    'UU_SMWGz0@2*I>}bRz3V$KD}&N+>Lq=c61Gmw<JqqO^&wU5GTUCbAe+1NuPBYnqfe7*|A%-{K1N1ki}lkHRBloZcDHdOh{Ils4Ru'
    '9Lv(J-3qcy=pS={d=qbln|W*StydfJ_=#R?c;e1=YtUSS?%3h)iMH&K_g9Vc8|hJ(WP{{v)f;#9?$s;MyO09?!KGltZ~bNW(p@!{'
    '-PQU#>kHzE{<0T!o7T!1<NYMFo56u-^vxM>FQ8)|-WBPa&eRWyC%1lWt9NTed$J&JtpVvv&K8OC`ql1;@-Molq^x~T4j$^t5BZ~U'
    'y9TsgEawNc6nQq@ZCNKT!8=JQBJ?Ebn$>pICp6M;cJ)W}aBAH`_u5tIK@^!4of`2Jmy{B(>om5FY9Dy*|Bc9z8(FmeQcp%=Y`1(e'
    '`!&8_*g8Git{)J+<IE4_obPG-W-D9oj-8CPYs{j_)9gCKyvbWUaLS)7{x|a)E}ijW)m!b6RoN4IpzrGE?rL&zR(YBDfZso&b;Oar'
    'SmS6pdmc14MBbUt$J;A-6j7!*c{J)c(rZQ<qF3ah559Ga%wwhB(G^5@$UN!43QFErG<TF}lULl{5VAP{E%jGsf%SvBmLIHBCeMgw'
    'A}cq6EGN(V)`Q$t%V)EeJd<c8BB;r`q%KN%kkD!QTX#zOsD(8P3Dtq$CYPQ)``t0&8q(9xa%{oD*TXfT_HVtbwVKzyxVCAuQX}4>'
    '@wN8Z7QXS0zoYfx|2rHxfnJ6@bF}|JJn;>l7s+bjrDpE2O^|TP(@U+q@7hlMGFm5k`qJC*TBr2vu7*s{FRp)@^&vYElFi+@tuAOm'
    'G#hdRqra*@v7TI2q@HZ7=DHsvvh38htM1sm%vPoWeITRlAFolS7s76HQgp`k-{vK+Nc6HB@GkIN&D-=yKkd#gvU1SlL>ure>BOC*'
    'FADutHx~T#b6ws4R9FAS@jj6G&Tl;L{{!9ekas-jj|@Ltx*Lffh<D^WQ=8l!J?XviZ_C(@=(#~;GLI2_()$C*3I0DYE+F}Xy@Brb'
    'ZS6=nA$Fz}^3Vp`?(zb9L-x1b>iObq%-su($<YZLt?K$M9_kA`^xJ$uV@KpetQGNtL;Tubl~w)sEyE;#LDv52_?qFtxxtSTQ`58k'
    'ozog_i9Y9UbwbxH5*dlRSD`0dz5Q?4mX7W0{Ms(v=J5bGoM(8>c>R~gJfroJ+i|k>N^Hhh>aN6g>)j`()*#tue+W_dE20`SpQ~7J'
    '_KOtVQ9t%p|1YqwBHu!<CAw<Sv#s?^H$TFP8kb5&Jnr-wpSLihipd}wQ;M8TFQhfP{skLOIudxZ$Nc-dwEI}bm1+|qA5WxzGhVAz'
    '?tGA6c~-~1pvnV!g16$3kHJ1xUu;{=%U(^DOY_XOulCrEli!r`*6)tVZLTq{Uy$c7=?C7@M}FSPkENd%HI8pne@p!E5Bn5q#Sr^%'
    'sqZiwTcOkJE$RJYyR|*!_6Rc5{7vQ8^qQ%t0{ScVO3eh!e$W2qss=?l>45xcWdFJc-Uccvn27&NnlEI4$Ed8O;$NiK@Yu*FAUWy%'
    '79Y{`54;65k2OV1;rdwTCHzeo^pyJizoriqI*9LoBgT;6tB-y6ua6~J6PBf~`RUTXAgq$dOTnc-u0IKS5v}ah#ucP5uVCawwszI$'
    'f6Mq;aI?iuROAtUA)NFr*$&TJ$XZERGoss?#(DwOcdZ_x?BScJ09Cf#LSF<&v${QfB*(vMds2To-GZCrqa@D4|C27pI)3xX?s(8Y'
    'q{AGYFt*47e?uHD(~BZrl-J>Ft=qbj+rMYrw=pE9lZI^0-eFAY?44;qn6rE_Yu#9mgMEa==fgU`)ELuXTMu9JGXBi&|7wgP(UZxz'
    'ayVL)taCQ%B78=cp)L8wb@IE)XNf_9XNq%sSeVy#821)i_1mL!&>aW3X7`WKwYJ-Nac~neK-Fq+ARR<}JJ{!G&t>_^Z@W+V$xhlg'
    'FouDh&|Lc|(G&WeUdqRfe$^%=b4<paY=6kvCTHxEZL$`b-^Wz~#K$6TD6vj4jVG?y*Ou5S)eV=<YVePYxlcCc1(hi+t6<A5$h;kl'
    '`Kj%9GP|_P^APdFl>EK8yhtj%XQXF^4-v4>%Q`Gd<1G080mfJPZ;QDrvDJl?^}L?U`_TzKou9;!e^;g|JG3nF8wc6yp}nQCt{wYn'
    'IUVI~6zNvN5_k0Yhh%4QJFa9+X<X-Y`wTFMKOGjxPVD;ho>|elcBambXtR{DGx9Hn0viD<C^2d!CYxUK81I))FUv|7F(+?{>UP2b'
    'Xm=s=AB0P|+KKexHE9b0tn0{aU0FL9pLjZekHTvPU)!;*Be%h58Vi53{_D0$(K`x$+kfDf>{a^DxXN-3tcR@c*49NX@MTq4&NjoN'
    '85USZGHg`W9DBH$E$?{ZpTMcV#ao}`M=~9@s?azmu~}`%9TdZbyZKx6(c}2FbwDM|f_~Gy4YtA!NGI_<Qs&aw`lVYlwXQu2Ok3_O'
    'X*Q1j-=YWd_}<esZm*J~OO1Rhd$_!#%T3%*U8_M;BYO}oxMHlD>OH*=AC!3OO;)&kHCEQKIWD#Ti}9{cW5|dVC-eA6?9iuJ>zo_E'
    'Xls%D#=fq=04u^agvGkGa_WyF-`SD*&(~o0AYZ!8=iSwOJKZaC`V~=!a4jrv=7Y-4HR<2OjO|pK<6pj_(yw;eqE#TagwOQL!Yg)5'
    'W;TEL%_nmu+sx3l-Ldhoj^ediqTkZ%&aZ2(oM&Bn(^@cX%O|UI_n<M__@R0g6(*=I6a4W+bSeKSE6JYueWOS7OxD6gMKRr9!hErv'
    'ljbhl|H!;HZ@a7dd|#hsEqtHn{T0q_n`lF$UvhTqHQTcMOfsS?wHBZ7h54si3HO?|0dYu1NiXN*Ae{&2_vM!LbepN#7710div07K'
    'CyD)S=KN$?<yq!9^t{*;{Dt;r>OC!`eVS~qmbQ^ACUqKN#CiX!tTL-TsZ~eMM8`8)6Oo(~59Rb&N<-PsOu=xpW>Mqdj0;O|WF}i|'
    '>G#9;`_^8S()$RNlte?_+M>l3@hx4;H78N#Phy*FzGX*SY5&1B6jq9#)EI{~S)V0NzFeQS)kxG?a7!cgo?PpdgrBqPjWyP;JuT#T'
    'rlSvc{wkx{tHiY_O`-*MQ-tnPp-H;tDs6sczG5d6&z0uvws;Nqs6K8_weO^l9&ZnBX{C?nPyz4UwiL?lMXMQgXCW&0^4p?6k(-?V'
    'q|)u7+$g+%NLm}bhH_hQ^%<>cP^pF%9Yl9=@7*&K`k^AY_V}4MV|^5RSpxgHye{(n%ZkJYBs+SK>|UE}YTKY^sQ1gtbL53CXLI#*'
    'SHbs6W00|Zu}gsX!CV;?ZWkykFG&_pUW?cL&-;pDtU0$0O1Hx&J|L?0?zc|&uA*M){=IL-eY*YqeJXV6ZOe<KvJm{2TubY(>afJN'
    '5f7mr$p9ZF+u}>_<MSzLSNXb0bPmSPb}mnwYAK<AUcXjL>-ltcqjO2_a`y3q7{u)w)Go=`P{~<Rw~}{kuFxf(ldW#6BBu3$Zp5?F'
    'Se?+1_s{wguSN3x_bp7G6B;J12VO_!@^#HSe$t)3Lg!eY^H1%P{HEw0fhiuXzo<kNwn<<s?`P{j;8^NaS@&O>Py38r#;G2B)aD2}'
    'ut=D<I1u(+(Umv)?av8zFSoj+CnVqhqAX%Juw(n!9r{yxDA)dUJcI1ofb9)-I!-?sU+sKKXq=-TeGh$mqrWryXEOCX+gJr3er#r+'
    '2@hyH|2MJ7038KdXvY?Edu53s68kfj?R0MV;e1NQk&K!6ld)Oy`B%m=6D<-&jbf|(XNHR|Cs*gTtXtGLIcV|xJ1uoNM$K_-iIYmY'
    '*o9{mJ1bg?nsHBOS_^u|0>1LAXpQ(xHvVG_nfSV?Es-{C)c&C5wsKE~*B54U5j*y*WUewh{c7iSQY$t+-x`wV{{hA@A7QEy$>+5E'
    '-5V$PLVaHN4D9V-cb$$_n)f*4m)17d(o^Ucl9AnPq@|r6pdZ+8-rV5Ub#8sR#yRmVW}~!5`d{fgS6b+!hOU+2ts6YbmGK{pckxIr'
    '+GxjAJ6v9;5Af~uqPAEfJFDgSNYn`b41b9+SHDUd$>)TfhFJ^sU!jro+kR<m^4c%2o7k0~_alF0Y>EwS{|<Kj!Wb2w>v0||9WUv$'
    ';|v%DI<56NmN#=){_Fh4?^D_rKJf9AcC_%7xpq|gKYPTE-o~kqnp}4fdJMZsg>QS0uN1#ryf=3bU%z^K_Nou=u`L6;u-&3Zn5EaY'
    '8tY)FS?yun8WY{ludB<pyA*i+vvDOmwd8L^`yi%!&#z&xFteSgGtK$CN8V=;r!k1!z5t=qpA!E~_2WL61L=)sefbI>R_@xF>Y~jQ'
    '^xloH4PBXUr`5WU?L_wt-YxvijKniK*$$_rcn-JnPR7UW_7WYMw(eAR8YTQ7ae&yJ#MhO@E}l>CNieLG7sYNRu}S%?5BVsg57%y-'
    'JJ5km`L}4@#lA%z!(4#pAM!1?CaY>3zj}b(!6%O}|AX3JQ)2SFXMYzlNBnKboVAA75b+S&3=hLM;=|53S!+3$q~#c0%W<*$v0Vut'
    'AM^K!HmUDuqZavvIsBnfMSZ`h7bt?B#>Q_hp1mgQh1i+aU&@wjqf54SOW{*_MbaDjG2F!>9{J|Vy6$e{SUDb2cDP9%NOnly`u`G3'
    'qpL}{;(D+9bzPCpT|e@NmH304t5KM@&`Qrh2Pn}}OXb%aKVoic=&}>fuEL*9+T{{0(I)Un^Odb(MVtv8RIo26l~25HIz+t-|IT~Q'
    'cuz$Et#7}*jm$qEz552|ygVFRt@~$wOk&>}$pduP_4QG!O2k<e9n*<qykS~NV>zrdAKjbSo#ft4g>=dAM0$$s9Pvi=-sjHZCgq3g'
    'hT{h2(?L$}-9K0IWbMQCedM1ge4FylBYwoa%#*iqr@Po&Rl&oGZ-I5<o%oWEa`8Voo}buL<R%I^UVtuIeT=ioAL_etvZJ3{<x9UJ'
    'kMZSLzJUMuxw%;7P#lvJbmB@g?NU<BjskkKt->$9=cYpw_U565ea^O3az`AbK2*hUro&tudK^99_+qlN(oHQ<HojDzgl$*ita;w5'
    'd_wmdS*+iUUv0Nt5Jwa_WPd%>_Y}}M0CT|}9`$Gdi`#WKj<O>|0RPvO-RKD8Exe>lp7cvQs(j|+v^V3!u?1YC%tw42U2$YV<Sey^'
    '@n~`Uh&Vb%9>auV4%kmMTVa?U^YN3|fRcmx%pNc9{Lin_zn0s-n&q{TyKbiMS^7=v%dv0-MsCmIujY1MGkjfw&V7uhS;rHOB>v~)'
    'SY#aIdOpp@59lWO_(uQ3FL{6u+XZ@lZhpvVqMdQ-ufxCK9q)*xalYf)k8*zdJM#T#ZSF{{|EdEw`&VboxnRQ2$zIt>Fp<wNtFu+V'
    'HZl6+z3M-GYNu{us>oF)^!qc@k=cFH$I0v0R^DIw72oG!-iBi-k8x-|W@;wBn~2Ba7!eVJzm2Ujenc&h5;r+N#6i<AoNWl-kbf~Q'
    'IL*<d*B(sHfmN`olR`Kds&=iG`6)NK`kbFKR&w|ck7*-pKd+^>gmjxx#qk&1)exNnqsEzZ6?W#Q-8bcPTKO&&r6}(|e_sY|K5|VQ'
    'MGz~oVOj5j+A5_pC}iT5*5-uP#b(WX>Qu{dw`S_;@ooGMN4_ZCN3&;fCjuNbBRe)Gok`JM4mDWl4%)ssrcLv>>&ryca_LNy6(40a'
    '-edk;*Uq&(Vt+l!IoXV6L+98W^2@sHkkjNi{eiyM5O)LC6Wtf{IcB17m-z)pun>la?wqmC^+`8ce2fb^d~pZQN1Y>Epn1}@ChICk'
    'b0z$a{moB77LQEZsY5rPu%@DWlJFmrE?KCzMaMXF0!rv8j?@z!FG+5ml5Uq-zPBdUw+THxI4GSzxU&yB4AJxXSv0Q|VSy{;1u<Lk'
    'Y(aN)X%nB5I4C+lBsmWpS4FxnwP$jVgvdD&o<P^mOWK7iiJ{!$n#6z2WRL3=KFO6C6VVl`E7ykORfpW#aObMwRUQ+wKn(|Io1>pR'
    'ZZNH<XmyWf1D(XUgYDh{HbR#k&YO2(^SP5%+SM`g0(nf|0=5>pzYdNWX_j~`2V9??bk<<||0<3~Dxc8dM%d8a4mnTckI0^fZ!L6G'
    '<ah8<fhvASEc>-tPi@}3H7t0o?zc`{`k}@vgr93{+~Vx$HG>n;>s85d3vAi)NtbbL4BG+jgQ3QYBhd+|zkEKCzF5v|gWhpL$3fsS'
    'lB<#qY~Mi#OzyyCTswAei;hWzdGO9!(#i5^TXksuwWOOR&1vzvtW^)O8n<h22`iqx>-N<7w8K(K?y16l7Lo^!^<e!Pt6c5KnC*0M'
    '{^13`Lo>fvK4jgKj3=~L&&Bw%x(cS>?K%NhJZe#|9Px;5SsM6@e7potGEXU8o8Wuix6|hwTzH&eAH&l4Qp~9HC})-)%>g}mpG)KJ'
    'Rky9dk;D2hzn~tEV$>w&<@&Tdjxz4@KdByQJsPKI)1U0ILpylv8OULkmbL#RkIMGq0X}7)k?o(r`uA<kA7DGTxz5QW)?7Tp;9~(e'
    'mc_m>*0XR-a__>YC!UdeSk!CsU7QGmP7^xFXDE6c@oDh)B;yzE=mg!7bad)3nTJG&zDVh)mgZliZ##lKR^Tu4Gdi}~eNEVcTnD4p'
    'T}{vxU6NdmlU{bO_dd;|Tt3;}TwTVaoY;fCH#gXhFqVp=k|Ru6=7{g_#{$gx>Cr&4mrjDkk*oRadf_YJ_&q-gPd>++v;H{`;y%wJ'
    'CMWXWW(({8fY0SI5gc=5y!7}w^*Gs1WN5BcO7<vy5dTYkGI1=$ugw3WqmnSTmC?s@Sg+sYMKZtfe8Sr1V=ei(io{>wK?RFu$CC*i'
    '83b==xu5!zfy~p&<H|O$;q0^L>STm&%Y5?G_g>xVoc!4TK0ijO$NJodxvla3B%c1L&K8}YdB5aRu}2T%RByJm<fHUfMrE)rSyr_&'
    '8Py55;ON$SU*@Z^^hdS4nXmOIhW=rmFN^Qo%;j;t@Majhzy+g<I0CtvJL-{qFYK9yUK5@AEj>gZEv|bed{~@w_e13f*Cx8mv)zW>'
    '$9`u%g3d?$Cz|9>ARvtAHL)k4o_1RE(a9b*FnS8mg_?X0fz|JhmE`;re3$f?UN3%JYpCK_V9lh@0w3L{<byu1xy$x9-^KWAmlVIh'
    't}a*K=AJ0V>srL+ME^1o3ls9^GmYIy6aB-A=q5~dVzbWIVi7hPsd#e9e#nAr=BMOia_lmTe}2@9t5Z#4a+6>jS;&!G&3brsg|9I}'
    'hjYkY>c2E9+d1|gw{R>UpF}Zorm62+L0#53dOn)9AnuO|*H4irRF2o<<4(ogXXqxq!CsPN9c8SN<OAytKY{SX9<f61bS*yTIy^J>'
    'BP{KT{rN{e_A_6LdPQ83V>ZH{Qv9b(Uz0zXkI#MXClC+#XY$qeWG6^gOWbeF$G(`jgx(MfKGwL{UUbK6qetJ(tmmihYF(UO>ju#!'
    '>A&}<IBi6&)y}%rvmIFFWBiCArTmnuqvj)#_ulpCIqMZ-<l@GuADrvZZJ>57<I8-`@cbJ3JM^_f&VhW4<IL6|OTC%x(e=HPStsAF'
    'nfj(x;O3d$IN_h!;11W&8w-+G#N*MA4r{W=j|<1Z!au)U5x>XU$nlOz$B}PdLcVEnqtEtc!&<-DjUO|{Q}y6R9(b;P%2ylV$JbNe'
    'iu_9Bh;HuQrU&^#-#X$^^vhHCpp&iRK2E(*cJ-E>pVK`n^f|5b5FN*heB|2kE@uRKt{(e_j{S7>RsD(nQgNv`w-38cAvbSPD`_Wl'
    '%W{B<F1hoiWbP*Ev+@i2DLt`4k+*Q`>ZSD;_$4`dbtz*rp{%<U9k5AW-ALGZ<%n;=BTbyXgKJ@5xV!rg?urXpOzMUBbR4lJ2`wDE'
    'CDysoBkYFb{(`+(ZyX%pTpckr=F_4$0Y#&G(s|PQhXvxfEqoh3T}3^zSKy|2&T+5?$Af0<*Li8Y2C*woe@<gi#NX-oXr3HX@$p{n'
    '2%f~Zdh$5*r=0y1zJhgC>CQB&lix_#*{_!4PPKgLkJrV1{8)c*91$`odw<fs@a+i~J_Y@nNqXr^IxlpW2J<71F(Vv>PVAdb5$nA^'
    '<z=sDrZij`Bd#kDYx{_{e*>@jp{rwWd1d>?I6cvS`Mf+~;(VV<5o<jPEW$Y<#ZKO?2Yh6*UG)X_QPF!tp@Zrn@vBGwqkapq1Sv1|'
    '_JVX%5xR+V<_UZvY@fmVThTv`@f-7OBhjC*9oSzc<G=W=&bGHlwxhG^YGO}6=dFGa9Ztz{^_|sSE*SZ{58^`Bv9nR-6y2k}6YHN*'
    'DNmz<LfcVluaf$n9qU8gVx8wT7slUUvudu4LH@3uq0bYpF{y{`5$BD>^D<0Y4;=P|OzxylwkE}}L-ci!M|%QqjyYB-PD?<n&*!6@'
    'D`)5vS05yC%NO4^LLr|9@EiM^BA%a}_Jy3sOvKm=oXgy#N2D(pn~*+3%%IOF)>!E2nPC;g8O0Irh^I#!+k_289-4C?|ClVN>v1E?'
    'DP3>l(0>CDs3&@Sih->=OgafBqUS1XGUCM*$TrPS;B9<QJlnm3j@fBP0wd@5*TF_X_C_0P|28ULyXcjGKCRO4;Cyz}+xzf6>guT^'
    '<;&ByI_{4$Z0$8msBKvZKlSD`4RPul@j7xDqzmdoH_Ys3!Z<_15{UVw_f1F^cVCkCV&ythVzNrSd?oX_C$H7p%;J)Iy3+}LA$qmR'
    'r8h30yTGct70R_AObT^{ev+;=juqeJxlucxuCcObE7R|<t!#ZK*dJhDq)ildp6)*+I!Nx-`9v>>@d2BY?mlCWHDQ4Q=7|%ukn0#s'
    'd2eGZd?TsXNlv`{yHC!t9Cyd%eZRI&e1}{6aTN66{2fkMBRq)SK+GTT#}c1ReqWKtWhSSi)j>D-sb{xXA)G5~(3^zeaB9%#OEP^X'
    '46No8?oL|+A2@pVr1E{|T7T-+23mJKId^Mi!j?VYE9TirqgP4&EXIHtkEdglF}lBIzmX5|wPX*=C-!@)=&S%fzq=W7-iK&w&bglq'
    '`G`>}D>d?S=()y8U^Z<rXY7vszYRW0K7DVRBfRrLCiFYx52wsD=z8{L<@1?NBh(M*=L2*G`^`m*<B9(e{$GvLcMv{IbaGS1e42S$'
    '{#AJ#VxMzVI{XAz@rgCcse-9qRPgkUY2K1CB<yKH-IT3KoGa|F|3!T+_%hoc=*7v&nWeovHH-Mn7kLx-gRS<$kumr?-w-t5T(ww#'
    'vfmB%QFM(@wjtbxQ?;(h+d3RihR;$#3}c6r{!riYW?S?*J%tK>sLY@LbNrC5(I}^*Lpk=GA0x)aeoh(}`5Wx@1bV?MirxsS?naCh'
    'C-D&7HJofhIOubGp7(*&btV1)pJT3u(!&BL`S^S)QXaRQgF)2b9uAH?d0~heS6V{{m<2JVQ7XULeaDybx{zUc)C~L0N#YxFoJXGK'
    '7Rdck3Lk+V!&shtir5?L6|-iZyJPlOxi<*vLEKni=d{1HJbS^P;>6g+$;UoQ&XJ3l1lMNh79ZzM@<MpzDL}rKbRTNsP`^~*lfe>9'
    '2;C%NHOXFw<kU0N+ltzcQDupfvKX6=DtsEuKjuehi1!#**}Fp?p`62$g$F#8<qZBhkM?nFw&-(P2}#EH&ewDr=R6TdcI*<LRto#-'
    '>b;$;mk_?iZI1@wA1J2*%XL8S9?~^)5nrWs^MOY=o*?&&CA^a8QvPjVqc2{iJG1d_DbMvCazb0eIjDCjATG{&ppo;D<jGuFy$fTu'
    'YAUDe`IKyW3-y4gB|?0HPyhP|eM_8fNOr4fy^~Ep;q)1tqv6<-BvvGU2Y!~nGhQ3~D&|P*mA?|hhfNZ;Rke>2?~HGIHDtB$3Kqjj'
    'I`H*`4!5;C9WF7<iBDu?oKad4W?Oa&M(AsKI!*b+-$m%)#LTMkZ?EYgm$gSv`XTAK8T^l|4(y0r!c8o+#=fHs8ANR)#>V_q!m;je'
    'oAvEp5!gEN4dh<pb)KiOuNJk%*fT*ka)48gNuMoApLDr*SJR+p`&Za|@c9RLmHi*+aLF%+2mI1RF0Q}+HJZqnfP7A+mONk7$$UHx'
    'd8(g|`Z*V|noU>u!#ZNw){*PQ^tREt4vyXGGxk%}$lr6!8hsW%kJ2A3Om%_4W2ogHvJB<=4Cia;CAOHTSo!`t(dz<zm9JjZ&EW-{'
    '!Uy~KAuSUep{H{^Iiph89hDScyNA5=d!BbD@jxr}9o}oydmrn)mBihk`x*JsgcrxWAD;J8v91y_top@_$MQO0DaI{MyK58uc7}Po'
    'pC(5)B{slyisfLoSrbn#7LI*6^=q^JNA*{ktclnMV#~L&k0ElO<K0haa(Pd3Wzz!LQk?c^qn7GS{x#}fg`Xmy4?8X1EAaTo<14li'
    '<JtL$YbUZHbjBVhk&+LI{L&Kn;@RlA&{>taK5P(Is`f}54@PBt$GWkv^fU){ARd6vi<lkwpuqVq(sz#DTio?6s0m(0A8%#<c&>Ii'
    'zhCb`{(LI)yM#$CuB)sh{vMzBnZ(p?bI4zdS9vE{qe66FoL`HgHuQCp(^nBr=<Ms{51<}$T)+0N1HE6H#JyE_nTsR7y_6%uN4I$-'
    '#`ox9#CimJuKYFI7nekSp5$fTD*sFFNh;;vBldjH(%P>yFR{Fdb#mPvVx2zf);7ZbCY&I8crQO18}<z~`1E2$4tRXX4WRCju;Gbh'
    '>EP-0Q?L4T=9<7lHyDKL1L8gSPSAkxMUp4y)7;X03_Xv0<%mxb{jT=)7d4-~E#eNqC!@s1HWv$D_NSeb|Ac**be-7a1bhsPt=4af'
    '9u2EZhd$VE@j=}=VlEEX7m0jGvKPi_mcpcl7k)ML74c*!>#zC5K@o$!&)Fy#T<r}Pq!={LFgEvj78oy?53QX>_?2XD^WY4x;J^R-'
    'kN@+30r|g#;{'
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
        print('Official city topic filters already present. No files changed.')
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
    backup = backup_parent / ('EK_code_backup_official_topics_' + datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
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
    print('This adds topic filters to the official City Information index.')
    print('This changes three code files; the sitemap index, database, media, migrations and routes are unchanged.')
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
