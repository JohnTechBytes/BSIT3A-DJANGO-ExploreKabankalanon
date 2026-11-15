#!/usr/bin/env python3
"""Install reviewed City Information code and sitemap index without DB access."""
import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import tempfile
from datetime import datetime
import zlib

FILES = {'apps/info/data/official_sitemap_snapshot.json': ((None,),
                                                   'b2ea5ec19f1bcb735fcbf655478fb5bed288d3e3366c15719197d58c1b9a073c'),
 'apps/info/official_index.py': ((None,), 'e3ff144d4f9c237b20cf7b8cfc3c0d2b1c7ec2ab02b2476cff2a70f419e8f0c5'),
 'apps/info/views.py': (('745d8f2b24e7b2260ceceae3f236a130fa4d7b7c6af972224dad5e3839e80d37',
                         'ae7d3ae21ded26227a533c8ddd97218414bd4a407de7a6c00dded11eccaaaa81'),
                        'edc43a277bc463f0e0b7729db9ec067135fc8a8c5ef52b4c6d08e1ca5c11708a'),
 'templates/info/city_information.html': (('4b280087cd9b9da62b5bcbf169bae6d7f58d94ab36027be8bc78e30845522b25',
                                           'bcde7c8decbaaad9dabfe7bf0ca98ab882ae6fe25a60f714472673cf6ad7fe5c',
                                           'b791b428776ab18f268febb035a52f377fd870b17151fb84a78fa4fff1bf7a17',
                                           '2ffedecb659539f7b55fef33e42794217a344bae925d5d7e34c12002a1ffe271',
                                           'd343d0bebd12b89e3c975edb25d0accfe769c0c0154ac7f80566423288344ddc'),
                                          '3b47226fa750eaa88968caa00fa31962196ec8054d79a527a530ef37114b1b87')}

PREREQUISITES = {}

PAYLOAD = json.loads(zlib.decompress(base64.b85decode(
    'c-rK>Ta)6<t|0nf*6TO1w{4(TGZFK^y-Z`%fVtQ&6JWXlV<=V^6xj3UkEBc+LxD3J$cb~}JXBOcft4vKmAdQy{A;?~ef;-o`}_UB'
    'KUcqwAOE$B{`EiqWv<NC@NKl3wZfoNt47|qx$cb1huPbD(KABr*Pz;-ZM;u^qc7*J@N>4RZs+50?M<wOw<$+vW50Aa&BN4aez@b}'
    'p|;pL^Hy`?t*QaMUigLnZq_<3X5;3;9nV9v)%=*%s`crlUosov0iOZ?)20B^d~1iUQI5PfYcYlI&Ra|T{CYMH57UXQ`5XA$#0zWN'
    '>T<RjeRNjU;j|UT=38~?8N-DKfBUV|@)xXaW|Tf)?Z^4J{Q=*7_r|@2JL%&y0=^G;MsMN4^Jd%Lr?(l!@V?=Wj|;Cb+Ig)}+&%7g'
    '^ICO1Ge)u5Dt+SL-uM*GTf-0B$GkO)0B4{6s;bYnRo&g3cD}J#_?uBME40^sRQ!SXt!=z$W@wA~r2PSSUUgvo{?>-Qg?qnMj^Mev'
    'zd41ojs5AhhCh<ed#xR;asJtX_x;WA;J2FF>9_=R0KA{S+XKArW`LVn!TjNE+n=*Rbv*@|c*ggG*D?>YaT(VgXTDRP6-I}7?YJ2B'
    'b{l_F-kYudf823tJBv#36hG6l^*PZ&Kf+!#q|I#85B<eEhfz7q3~w_X+dFrB`VH#>o>-he-`KaEb>9K}#K2RLYb<|z;}YOM4E<yB'
    '48X%%HHQ7|0QaFEl|E*M{Rf`4&8*dOG`rIu_J8-Za5x^7dxHr0sZ|c9#%Mh;;Ja_@d(Yd?jD9%F?xVpzpWwK&(E;b94?n8zW)q<0'
    'w#WE>c*&bJ*!QqGsyU6YKGFN$urYGXy0-X1&kL{4NQqvL-om3dC{;(z{-8Ishl63c+u^)F7?(D%o;~p7Ze|n@^jhzi{MPW$A9+nD'
    '?ClUHtZieq2nOOf`<-{-v(tPGd|O+8tF0;vvsM9aYdb){0-OoXkIT@jRhRR(e&mjAcFtPB8?|aU-yjd9=NWjqe5Cbn;Eclg_l?og'
    '-|(}uUBh`C73Z}gz%YLRtOZ-wdhv5mCAxXz{%@CL#$sn8k1|{XpS1tu0c@ZL@XJZ_Cg!`}`Y1b%a($qU8WYWKkDB4{VdG=h*?2oR'
    '8`_WBn!|uKzO{EKZvf6s+}(OU#|Qn;njAgA?*jgJzFyACh4SdFt$Tyxg7B-CwO^BJIMK_yS)lhu!?raT+P`6az5dAh;LnBqg_~sm'
    'c(y$8+Tia}i2LHt2+T(L1L*JpaQ^`RX*2klwuX!O+x!#H8^}>O*Q2%hhI|1s=nd(2`Y_@D{^sKV--pkSKo$`1g&>D$?L^<oJKKK*'
    'vS0#owa^FN2Aa0uEROXMWf#B%`VL{=^8>6I`6PmMzXSeI_AWt2qAV!Td3=NS2Y5f|pL1MO%l@2g`zSjPY(LcxZ#-YRh4A;B_`Xs$'
    'Ys<)+G<6STcV|6^(^J}dlis_zB|cyM7@+J#o?Rc{o`|NC%KMKVTlaMA!WkcJfoDsT0)2il+mtoH`@w8hN4@o_-P6k;530>!{Qe`M'
    '_3d?l3}$OgWsyG_g@})zgG%NcmEQWJ9>~oR@L&4`>so+JT>!uDI$OMd!sCxxIO_(Dqt(<H%r_fxi?q&rR_rBb@8&ZTUI(7aJTKjE'
    'ZLzw%yUY)>*5>Dz{)RiatS5iNeY@&_EI7;O<LZZ##S!pc6KFZH0S6xN3-V#*zX@NC26%`2wqPybJ^(t8ig@=j9vB^b1MZ?0@+7Qt'
    '(hjD0PexU^JDVu058lMTg!2aH8O|T@8s53ptQ>;(uK8_0oh*UpeSnR8p5UScyx;#sTq3`B7VqiVzQq4E?TNqMO_XOflXxnTX_Er-'
    'WxHge><8TeKBIx0S@LJC5<Z0UGsH7FD|m=2kVF1r3bF|J6=gl@OmKF3bgp3kpI)LL4H8~kz&WM;C$C9wg1d_0?9Jl%0(|3lCU_>B'
    '8hjt=xKDJE6yLzZASVv+gY?s9Z+*Den@6C@63+i_wzc8&L#8`5nk%^HHKYNoJ2|I2SmT)=>smR(Ki{%)^9!!vzDs34tOw2~@FU#8'
    '{Cxf#WS)D)%c#$Nxjz%!!!!BX0@6#~NY?-RVlA6;VH~x0c&~DJtBLcTybrohe>tnQ=h^R&e)`t_oa5cTs)DQn83Sjtv-Os<H#q;%'
    'VwIKoD2IUO4>O|e@E!Cl4bD!vXOuy|1G%*c*YKGgUu*dipBHlF0*|TQ6M-x`-)Ep-grr0MsATw=$*}&9w?61FC%T6~CqB?!u(it9'
    'Gyxg<-E21Akw@G@d*{E=dHFpt!T^55`on`C>(}esW!IOLx$yiCq#@qrOdedw))a@x3+H{E@7*jue@?#e2<kM9p3LTe`vqi4on#Kk'
    '%;lLzKs(q|G%;Y0wM)8_Yy<ro;L+cpOTb;iWhmEsTpjeo7UGVrbsQ~0w?EN6KWjBt-uSqqdvjI2exG>tmJZli)9WGb4Rp-+8Q>W8'
    '62#jaWXya#yvgSij$f|;ya?X~Sz9)nd(NxX4c-S?yn##sTMG2;8u2aDRmL{xR?AQL9r~B|9q`F$PrTLK6aK*Np=T0(;EuyJUErH^'
    '7vjTGXG42R?@Bm#8C;Jp&J*qvbewQDu`c+V-Cgqt&h8QPse?PI!tc`h$J@t>J=gq(_t+WE5#;R&WX|Zr4BivG<K4ygLZ1g7)Z^cS'
    'L|+2g3c4Zaa?4q>d?Z^E=<00B2an_T!X7aIUhU%UKf>K?03CJE|FX{l+v|w(2JWt<HZjT@IG4e6-29jnM$zo@8MkET`B_);^Y(h~'
    '=tP@6;Juft6Qw#rE3-y}zIWCYxZTxVe32>HJ)@1azL4kaGpM)HosR!YWsQ-_toLjA)4B27i}jLiKKeb|j`l$Bh@N{}M`AQx0dEA2'
    ')z>|f{Y{^l7$toM=fhu>K(}bd0DA{I6zNrjhbx%C<1xq*z?Tj*;<gFM*4b)#^*qoASC!HY++BT+c;aMcKbNIRf%zkVr?R&BJIWC_'
    '!yqq@3o96ctuqhjoR@!Gtr_;8r3={aF6tOtZ&W6G;YTZ7^VhTZMmhwO32+91W{KYT?TTOV%rU&<IpnZ^_rC03c*kAfY63dw#GaYk'
    '#%hB4ccQyA%SiX=*X`$j;iIo~;JN^_VPd%V86Srl;`+<?zv2aS<~KOgaK3&<=Hf?m;dgmYo_mG+>$MTSI-BJZ?Z{N7M2p=mz7fbA'
    '&Q~Ykk&pMRydYW+O4;vU@!(>YD;F3K9;U5k4BrWVy}_m~Z2%^tHek~?A6gremxU|7t*y^@{AQ%hC+$P(J6dIAAKcq?=S5|*%O}Rw'
    'UAtLovoYE+mwKSN&FB=&_p|D*s?4^((4*R0&<%B;K9|Zb{A~LE)#usWIVv+9w1#&OlMxwT!S3oiOz&)FzVik;`Cysou?MCXjAF#g'
    '^>@k7K=|Fqc>c!6FZ}cG#8&QR^prbyXJ*~@=N#|;h}|t*H~BE@l^x=p?5~MOXFkzeemdG$-EX3O;TNV;GyPepr)2lj)IRRgv5@XD'
    'M*k|<458QLy3i%gvj0Ed!?2IDj5}u6y!v9pu+LuJVV5wz>KTaVFZ_QA=j&aMbog>lU*Q04IBy4Zi@)j}$V++uzk+}J93xKe=r#QN'
    'ZyKD}|MkEA^*{c#|FzkL)BP_VB=A@J=zrs1e>T(o>V5lP%l#(&*Z=(2uV}cyC!&T2H_Qqx&DnVP$u-OXH1?&BlIN|zN2|LHT!i15'
    'waQDcMpiFS%}U<~ZT-_VKEPrPwHa8E?TLOnI$-@Mn2k}<Z=F6tvUGs+mT+>wN^Tx#O|YKiS=Y}7>vl~i8>AtuIs83A5AksCfyAFi'
    'TzZTV-uFGDZZ(`n`WjAsz%2jup6?UjeC($vK{g;&2ReEr_TJ<pM2*^OwaF7|)<)&p7T@Eq-|RorN%c2*RuH~(TEZ#)a3^;Ba{ydj'
    '(_`S8qq(Z02Wj(jU<R;nI8{1Xaj40gLCK-dy!Agb-nZ`^qw$Y$|69ZrdS}s+L@9wd!1aX(*8r&kcn3)X5>5|0dU@qz^q^J(3t0a!'
    'SIK8{_6L>}NW#z$lkdWJhL6z-X#R;-F-QftSx`C>Ph32MdzL@UMkz$A%8#l)T?0KIBeax1gfM`AVV%F-f(<9Dxj}fir=Kml?eOOM'
    'K)Qew{P0NfkF+yw+W&43GJI^<z*FTIEu+r3zeLY0KDUi@9+*PfpyiGp*h#@IfyN)s2E-qv<<ZSq*H-X;X@;L`jlwy4vfzC$&{p`I'
    '#1m!K=7C?ZK4EW1IBOBy(D-^w`zp9)E2u<v&^TFjcaL7=c@j}0Pn>oF{=$9XO}(P%3a-Dm!}s`Wt`QV$?H5R4I!C?t?`&<ue^9c~'
    'IRm&~&r{`q=Y~ZG^i*;K-TrO1`a8b>H_2rE%>!-hR~>l(e%JH@tnb*}&LekHfzQpCe*L}Zzb)Wz9q<gAb?_e9Z`C5)Yzr%HAMv}S'
    'y|zG#zkvk>@VtS(2JQ1tXEXZK8Sg$(Bk?Bbc|Pzpk=5IoFwGr4yJXsl&TfEO3FQIX*CgYWY&90Y$ir>}&YPt!SkrjM0p<qiRqRIS'
    '#S6D^j+tc}?*cr_-o(T`;Q0pL3b)g@-Z#76r}YEA)*e11elNjZ7nbAE`!4s0bc5#c7kUBVY`{4SY{xRJ*w+9S-t2$K%YfSR$~sv='
    'b7ckVf0Mibp6IUZjRm)^=OBDIv)kStaP-Y{-cN`}c*X|hO=mI>fhXVR^>@Rn1Mc7Ys6p=0ikcPLEXoz^D53%1DQ9SZaSm?E%Dep0'
    'yru!ri_ZBzz1_Fg!gY4<B$HRjJ8<?%vqU)wvL<*Bx}cGCTb6MPA70(ktk}xp12EziygKmI8)`ei>jtcCo4p^1_WzmTt+^Qi{kfdn'
    'u(e(Di7UtV%dr8^9yj(bJl980KAv;>PJ0ekTS{-h0bi?CayP@G8@ssgrEBa-lLf8fn;C~I&shd`0N*ppA7E|5dyOMlnI|u}JQH{L'
    '{T{A?A8fF0bOU&N2Qn+fwV_v;_}qDqkw<+4t<v5iyN>iT10A)J7&OsuR)Kh|{D`aoyyKY%`3H1=vjf=s$E>FB;cRcG<072r^06D3'
    '8p($&E$`6je4eWjXm2~zJ>V=S&--TMxvN!<W<7Z(;0k2bY~v@exGYL}5Uhd9H){g&=nZKWuFV?q+wf$M-AC7ip8+}jov&@NpBv$N'
    '-dcRK<54iJ|0QkTP`iaYZJ-11!1~@k&RG-Aj@|?M(C-d;`cN+8d4~PGjrPD3-+)(-a8|V+b@Kx=GeA!%{-{?ztg#pU7_1XHeX_Si'
    '>lB|>&?kKUCH=tyE~9rDbd5fXh`w2f3&2@_jZvv?&?u6e460mCHiM}_-pGSje-A9jJh_2cLV3Ww#`kG-mJ6ZP8WudK@h~s>1;E$1'
    'iQZUzuI_JbkWahg46FmxHxM_-w;&UDp0U)rffX@+63gmtuB?7?y*JK$=Yi+_zd&}}<Q*U7$60?kSzE3@0Pk>^>78s1iiYhxe8zTw'
    '&n-p>E_H-C$o(Fk6a2j=y#UT1-Zv<_=VSc<dIDH})zAg&-CCUx-+1=lt=jSAZOz>eSd(XfZWJ_(YkjE8^r46O0M@<*9f{Ej_`w5y'
    '?FN;s{QGv+NuD@s&#tc(?!7Dhk?Yj(?D@`n>%UW^zBYu<ER!=5Suv9nNoGc8?Cs|DT^cRBp*I{|e2%kzYRxXti)Wsl>6P3W4wqfY'
    '-ECM!uik{SPxcVlYhWKvb|LI1X7nbzC?h)>2Rrz`q5EdeH<N3LtXkUR(b_f4d%B`d9>5K)JN?X@vc}MBRDwIEyz#bn2sDbHxWhq4'
    'qP}Sp|2~Sl`)B;@Md9b82=e#LYxU|E8${+=o$(2HxQB8AJ&hpKnT^%mls*~0GH0)zJ(uQ@?!Nl%dmQYhl(!yT)2y||bxEA(zmgA_'
    'MHGRZ_c@QaowsQoeof}@zz>RTiVO{z{g&Det}_a~mc0V_8u|zTCS|1ZY_4xveoa3!LB9yt22b2qnM|FV_ol@Cn~CZqUeq4g)8$}3'
    'vG(&#7*EG-xRdbAmi0M11GL5rEi?8-`Wadq*aUD+?1%UWp1)_=JQqC5d<yYxnV0Z4=%Ame%`YbpGI(I`Kj33X^sD=}``@o6p$VO('
    'zq8Z1eF3`4rM|Q{b)80$;R|pzPVYF4+wvJ5d3mN?qq_IT{hd2lUfL7E0%ggL+n#@=Uv<W$%X~bkBjws1XkXxYLfrqXm6>nODgL<S'
    'U%T{8roK}8-%q%EF(bk?PD{UFmCft>ZdKiRV2gkCzZTJB{vG7a(xa@))PI}W{Ft3Ki_Cwxm;d{;-uUNc7JYF1#Q!Cq^XsKX>T6zA'
    'FMXY@xjqFsggyg`^kb&i2G&2uY?2<&l4qH=fS2P>9)0^sS)tmkeI}V`E6_tgFJ6A)elZFUdrvap$|mCQjWQs%^gZDJTah~M=fq4b'
    'pof-5TsXe?TEc_>hM8y-=_zCMhh?*2#J;(w@4+*8Gz$K||M!=u@t|5JI3Pb<WAqL(8}B2wPM&Rcjwofa0v&D9&O|?Gy`wanE-N=j'
    '!*!Acbc&1bwGHDf%<jGT&P7#0lA(A0d})oDGQewqU*_ZCQMy;ImF`5K!O?7v22K)*d$XAj7oLxP-(f<F%WQC>W6D>B#J3OYg74(g'
    'ZL@^E0^C)GZs+WR4E<#G$+8n^k7LX@r*%+9V0)tf`&U%G9qoJ5%h!1RnMU5LxPP9laO1m_u`|!$(I=UZiKKl`vcQnX;cRDRILkH&'
    'N&|QvoGmzelp%Ng<lp%x8{PYv?7hb2$@z}o^9W(~Y+mYKN#<PUeDLr5bCuQbeO9P)ys)V3&w;u6xuz<cGmr2La*z+7EJLs;@f@BR'
    'lF;%-))CQ>Wg1YNAxrNo8vQeDk(~eDF?f|hhR^7yeoEGs;iKv&=%5tmpp5Vv8C5?Am95```+(6h8^uoI8Nd%1Qz`Xk1zYoDpcmik'
    '&#R1$pGgHo5^V>(gWU$tnq&67a2=V?3h~i9e|Et#sY4?NKi@kA{;c}>{i|nY&TU(tzx8n+EE5xBS>yJ8I_a%`hFqT1kDu;#q|IAr'
    'JOF=C^+NJG*>5&8;C$Zsp4mOb;!JOqe^Qy#I(^QJJ!Wpdqo3Nt%BYJh#EXpUB-`AeyEeV^jy$7_st>r_Dg&O{#&kR?bl@I^yYrIH'
    'sN=xil6xBVLiaYDBO`lf-;C$1Fmozgg6%^Y7Vx<{m1>#qBy_4{Om`W1V;5xTS?2s4XZKmk$fwIn1ls={d1>Cd7Y1-nL1*=yL{?^>'
    '7k<ZTGr(nl6;QWirW9>2st(xs0^R}LQ3t!C9U-kQ<;3|O0U4B~FU6@7ea9W7aqj<4VFo&@Xm~r{9ar~1=|6YYyTtWoWGwMx8?)f*'
    '`_s?K4SiyA%4UBpe#4z}!AC64E4oW~6~^D<hVyyt`=WoYJe0u^&(xP%8~^NI(~VUPTvm3<tSxg_wja5N|6+|9`;z4XEUqfA()EH&'
    'JGc|~AIeI5%hyZH3%%s;`HkRZsvd6W-buCHm2P+f82!~Rx^KvKN<Oz|at!1Tw<~^vEjwRTSuRTqdVA{QNa0?5hdv(^zx%Zt-x-fe'
    '-nbpj3O?uzScSJ<^z~7@-xxV$O9ZEPi`zqa>*6*}@;|`+B7*N8;jYo#v9|#mFspwaC|3mV%lPxs-eEEw>BrX1f0GQqy$7^m8mpgZ'
    'Gw`hTiNP}9Q0`snz9=g%GyUF9N6>d7xXX9HHp6e`hG)i~D>YW^IrjUkFi+M;S?P%kO*8wO<#UAu=LfEnvW$HCT!k|7^S?v)Nv4|S'
    'tF6hOb(fFM_+gp(9h8AQOTWXi3PI*&b!URPo=)7Gd`nrAHH?ik*XCE<4f!NPo4oifRy*`=J^SCx2Y`Q<SVa!v9dsDrj~)7te*qtM'
    'oP^eVFG)5ed=_~2-TJz=*ayD4{0^@!zzomLTm#z*Y|CmEKJ)n$5TB(j*vQ|(?u7fI`9Z$q70(tOoX)gc!85=X@IfE`qPv}WIDHS!'
    'j&X;syRUkFhKDj$9h?Uayei|`mf^Z!Gs65J^4Wi-YXCC$D?Kl5DZbZ|Hhse^-x7TH^c(ey3x2))`92-%TR1b33;gh_@R6+h0Jy{q'
    '<^$}PXCgAY9?l=i`}6rkc#}T*Eb0H0KS+5oU`w@{-+m3g*h0BF@x|Ke)<2hPV!4NK9#D40KW}B8*Fm0TWK0Kra)upEC)Lz0&H7(1'
    'GtUznihp-o1zFPn1UVI<FOKr@dbhLPL8rb+H@JV-q|ay9^yRsnC+m0Vd#N{H;i+S!ymN~m@w>#6*EaMuzoWk{)rT{-1=5K!ia8%$'
    '_*?jT1otWW3bhMfKv@*r*R$Iby*rDNN*BDp61(D3$LDML3;mCtd*K`Ev+fd$PE>7S*86ngq3<T`pz&)w(j?(rRPdAjKP-J--EGy&'
    'D*x1PSn?+Q3%`)F`F>@KF&*lv!$4+z>3L#z`<chTU-DKp2k%#BvGHa7N%b0LlWVNA2dlU}SI$&Rn1^+)hAl2eZ&=0KM4f_H5|6OD'
    '7AyOL8LNt=s`|t)d09Q2^*LRwui2+q6yC2OgRtT@W}Qv+oBlt_%OxGbPr8@vV7+9gnr|W8dtdN$>+FG@U&-?Fz596i#s2(T{MRpX'
    'kkk9e-S&ZZQaG!53v;VR%h^@lDU<(m(lNT5n;j~6?rC~{%P4bi>(eCTL5~Ff2O1`ovFNLDof~-Le0=T00=wjfe%RKq`Zv2jj4@zU'
    'd}^;}eBIo?9Ct4&!b`thkcF6u?{QuKr-6F&JoX%&D(=Ci<N40R#gIS4thqtAJ}h;ekF5Qa@4Km$k>;tb)j8wupR<fSe~;TZm-6-P'
    '(q59WeQx@m$(M3l550_UnThSj{Lr9Rd98No>*tvMNZka^ev{)(J!le!?iQ=J&3_!tYYm2WyEi;8M%t)0)WTsud#}~ccFI*e^}<eZ'
    'GI7@XaTzlkm#JZeIm!pD&Yx|XN03#YywacK3V+TU#cnpGJ@a3cH<$MFzgLSkbt+=j$x+5P+hP?!*eM6>fg{Ldl!bUEeqz@SRyAoB'
    'JGDw=)lDPqdPF}M9||%4TqKz1XHi!I*C-!JH^u*@9X!x?-H+ip?W^uay5FM8ccA4+n;C?Y0AshmoDbYT<tCua<24d+&f(5zH4XC3'
    'Vb>7@?-H!8q)twIcwa}q8|r#4#h;5=`G)wlSlq%|pbn3+(<PZZ2iZ8nxI5y4btqzSjw5!AIQs<==ONG(;R3D-BZhxoJ?}@w#n~T;'
    '`vI8^_b$e~kfx(i+cI0sen{eL7&8UkDhAn<;*rJJJRLh(@h&)v5x)0klbzsB>WscEl+(REc3hf{;qJowp+(&s@GhWd!M*~}1!6oe'
    '*ky-3o8f(CxcqhE2c-@MtSc74bP6E*()*0(xv(mB&?ow+m&d%jPwGRt)@u^`HPvZ@jNfvz1esTjyQ}Y?z_%-RT>1m_2fVQOqGyy1'
    ')G<3(XNlQ*)q*!}6JLWoTK-(sYx^kcD{8-kesc8V_s@=zJsUjEyqSN_SEb{$Miqfzi;oUI`e@018AToLXF&UFcKA`*03CbAa_Mg|'
    'Hct1%;`ql0d#91!Q`5J;=D%6rI#Kyg*2losTiVVF?!j*@K6!_QU|!R8Kl+Zo5R4fw-NHqDm1H>8A=MwiSz!(~c)~B0!!N9@2}(b2'
    '#q<b&*K{I1|7(S3wksHR3QPSSoZngJmK5#+@8DaNrkP4*zz=r3=*!u>7iT)vKW<damRD2Y{du!Ya^%X_q0efU{)4OxXWb#pulMJM'
    'I-!9~(n#m}y05Qx4c7Qv@I2v_o^c?Z25|@W1K6R2vn&4s(B%}*FkV^Deg@-V{ohIKko%Gm5B&ewWsJ)yj0+(THP1A`eS`ePZe=^5'
    'Z|K$EiB7~1gVOnZwC5%lIxF!!>htUwdiJwxl%LcUAf^A6-iddpLHf%-u(yw?b5lqCV&lPQ^;ta|CkFmo-KU?=Vt-%b;aNX!a*we}'
    '_<MS7ZbdcPCmDHz^vV4^`M<(*l_k;l%GZ1q(*<5GvREeb7v13Vq(Yl~N~kB?{@fP#86I5BaaxrQ^RfP$<B9np3JlgY&r|&IPSy5}'
    '{okqnWcs#)&%rpLQ@U@D7(m;E7I*9=jQf#IX^>xS>1R8|a5)4v(B~X<`!qj<-BZy;Ed5eH_<BEG#MLsq6O`)Q)=RrAv3MH!IZ1A3'
    'eKR+7Zz(<dZ{wjk@qin-P`Ntv*Se6axWIk?c-F_?tU3B<2)3=+A5`muQQy1F8Cpd7F;cVzF*lELg;IU{Yd+W#^mxhzT>%Y1ezLRu'
    'b71Z*wDWlG(ja?ZUhCeqoBresj1YZZpFsO6v%A|`Ha3i%LqXn=zRJ5pPNw7i4lDmb24NRHkco@5+u6JYG8BEUcqT!HC;AoWZ3WEh'
    '!j4??4d4`H7vLYe?;SnNBO6rV&a9$Nj~)CzkpHlg8FtiTy84j&2!>hSU!lE_?V@(&3(0h4B;6eIT(Qew3~~Z%YN&%0r`?Y`zJmL8'
    'KNmSZX>G(mKe2lOp5N^{iRn<D?i}uuIoFR-p8*^nW@D^bLw|QtH*)FU2HpNDk1eEnNwf?6R{6km)5Pxty6t9!zV{gL8UU@=_<t8W'
    '8_@klwoBKeScbJ2OzaOj-%Zf-4DuhO_Smqs1R8}$AI}Eh2tSk5rkf4a@v7Y!*ah9XS+b*Qi1o7>yzj947}sadx+kY2fB)T`P`5Uq'
    'LkO}PYyyx&UizBb5&Rh#V}idwx|C;J0{We_tR9E?x1e_fX-8eE6>5{;Fr&}J7kc~I_jX6WJ}u{kD(HU41KbrF$Tkh`86EZ#cYrT_'
    ')OFu1kh_gj*I5_fz2zicL|te8+j7=`7hd~KxlYaXW&VW?`)^|&>=(JpeZMI`W&K!*eS-QE=i$<2jzB53UC0l*<+TG_3uSZ4mzVc('
    '<)4ueVr@Oh$`I~}(sG7(PD5XM5q#dj_&Vm6@ot6<?2d>wE%4a*`(g-o9+MkQ&{weQEas4+E^@gpZYwWmKr76dgu9Kc7j(GU7VK8T'
    'hqK+dlxM&fqjA6Fj`!3_6X<kx9%!#x%2&UxY?@WII@^?Xc>a6?>&UPx8OT*5tG^!?tYaPW7_)u-h{cK0x>B&8Grnh(pIg=)=<2TJ'
    '_`G93f!$duWaKAy4BdiFvzr?0&&z$A{{UW>>E3`>V67O(Im;5}*SoswkJyP9Yj8gNSS+6gXcK_VljMaE4#&&SnbG?Te&I13)Yo|T'
    'Rm!)+PQvWG9@stKqx*r`f{aJdcBju`cU<bWyhr?Mfb%e`+ptb7DK0{n(|L$-Ld?sr9T&Z^j(!a4n9cN-Ir6{``%O&KeHKCPVYkQS'
    '&QH3zp8cojU%)f<hjqHP&>jdVH!Z5h=rebjKO<&cX3Kb&EL|gAAM6u-C?3cj?neh&p$`Ld+Q@IPy0|}?Ut?lr@lH7EO-5VnEnwEo'
    '53}AVbshiTcjO0k(ga@NonwIa0oNE8=&UM5D_9r)PUejcoh|Ys=#iA)UIO{%f6kHKgYxCs(^4FQ{*OM##LmBg+u(U#?Hi*{4`i(0'
    'T9znxJ&}KxvG?Q8^+nDN;fK2S8CZ|83^DIJxhJpbK{hhTIXD-47vTQlGH5V9eR|Px;f$NuacP;Hm)@pXawqd8bwUUFdJ(((;J(1R'
    'D6IEkomi1)CtQBM;oVV==#E5Q#s86wQ!#+f2P?)p(x%RQcwiH^%6pLep}(~bUt*&<z9-PD4)e@8rEZW>ndDDLyTDP9#cg_DwRjFw'
    'i#o4vy)ntW<CObwp1ZT`59}m2N4w%NIkN=)oANIP!?2C|Hh*5KlLAiH)L9ekT@U?)MykU$K&FJ;zC?Y~MjtH8oop=T2Ig~Oe5{J{'
    '<TLf1Hn9F~Naxepfc`etS8)CgEXHLgF|HMS7UeejST)q~Qa>v^8+8+ajs8unQ+bEK|73L)fW0IhT~$F}_b3j6cPPjate4uVJIg8l'
    'uFi7${&igQ1w7DRQlA^6S;81qjt)HhqLU7)4)u<quF5v(DovgI(Hqhi$v5UlmDmD2QYXF5oF*Ee9Jst^>5f9Z_Xp^dC9`gwc#J@2'
    '`s%2Z?e7EUJ;DzEprgiS{cW{qTcwO{eViF>I8Sya7uWs--Uhx2HL~MDo{?P*YjH?6fb0PN7=iBO<5Y*_d(A$a#r0pEcmK^^X8pfp'
    '_ZjFfvw27T^3gZuLC478J^Fs?)+?IrG<2(8Ibwe#Z_GO%H>*x>kij3v>leQ&kGG{X&hSG<zJEW{7jwv~`mEK=cG6#CS9C6ec5XqS'
    'ud?-lZVoobTb2474OtH#%mWR8rq%hRkM=CtMu}W^kwzD=%Nw|3Pgd<%>^e86ah#`U)Xk$6ppG;;z+U3Z7*ZpBKj|Eo#*YYZXs1@O'
    'zt=~S7m(Co|J9i;pbnh%xuczGqpvdH&qY4ix=}gH_n(%tINJ5$$#yD7t7c+;dB}OTH`E%5oyBy(l*iZU8vPgOnhw&rFe1NX?)@ER'
    'Wmc8<qawdAoO6-^c>WIQS!sa%za7EazcZa}-24x9F>RrJLbXUKT+VAZY!K{|h3C)zFdL%-_RR9n{x8H+2iE#ItLZ2+&~Dz&vF2`|'
    'O8>X56vo6#WpYxlHoL^-v*)piv74Ep=j&A=;em8&;JZxUv(Z_fCjI-k@R<(@c`BsoHDjjd^7~i&OL@+GCcHbhyP-T0io?!m9T=Cj'
    'b)a9A*n=S7uzUP2iSuP`LyzKur%#{g-#Y-k(MAC|9R{Gg?*Ok6t`*N7%Z2&QI@5z(fja{Iqb2lDrLj%}?NHFifnEyvA*IoUjBfF@'
    'PcG~jTGtfqoU>o#`TIJ=yr@!4y6dIvMjvV9;+?yNHM{}-oZS2T$_C2Pwf#waj(go?dMIHRRFGM-tGZ5*u{D?Vc3ShbG+@0;pdn5e'
    'LZ8wyJ-?an72j)4MwiE&6wOO)!#DEtgyfs6rTNub#&@-xPTFh|PK#nfB>%0Ta<b80WfO47C&hK=a~zpHTgOQTU_Zh=gz^@ji#~}x'
    '`p(YN3qT)%JEjiw-2l8jb>W||dY(il#27vKYS`Xm=C>t(E7tA8UO}g60pFqC3G0T>V>fJNcEkwQHQU;R8-5>M>XUCbc<Aige}PU}'
    '`kXW0GMw2FobglmcQOt8H6RaEL(mgG=zj(K6XQd3n%Kc?iz^+H*$0`tl!Oj!8rW&a{Hs7W)JIspB&&-ka9&AeDgCdCeecZ1Y3Ty&'
    '<U9{H<%2t3EQSCZ?LpuTk^`4E66G-vuX^ZHt1+GJd`|m2I1}qR`Am^7M#z^z#t;5-o&Z}(qr8<7`ufYq8QB<i=nWEI5&!?7n*5*X'
    'YjsJTgWd~`zx3fJHS?>B`;qHAS9pNW`ar98aH)%pj;tRmli_d<uVi?l!+<VsU`)9bcMJ=7$^3LSqr&6@Po>{j%ZPcTm@ClP?2cZP'
    '=5x0|#x1>z+?Eo?60ZAslI`f>8LWwOy?^3e2Qnh5Wxe9*I!%=s<9R*ev>?if23b-9zNDTnGmJ+SY|L!}KEIcvLiP{JaK<lV{RY2K'
    'Ebf~mPMA-CKL_@lJfCDo&N^@^A9ZZT*vX9g2QqsYec5mZ;LHMTw(C#3Ry<OkjAku*;d+6unU0m|y)jN?!IJbb$`gO1GX#3-Ja8vp'
    'YGYx2T(@wty7JfeuJisg`ht$RkswR&;*#H~pXWW6!;UdLb+nAlhcW!{(*AEd?fOLHePH$SMIYGCwtC3$qK&y0l)uOPqU>JG+Qnb;'
    '_KGX=_p(@K89Q(PLZ9K~8N0+=#y3EHo@&+AFPsk6YKF7c_o5B5^o~w-K5NYPvA^N_XkqNLyUxc+r&;E)GW)k<*a7B&V?NWYRytx#'
    'mfI=(`FKw=xGZn${`!D7(M~ncubrF?k{MugkPV4GW}}Vq;$<i99jqGVQq|2y+v|+%s#%Bkm~71SWT9M@!jx=Y^x0uuL!aVZ7k#rX'
    '>j@C&y1yBo^JKF%2Uj_zxqYI7(hzeb%*5W?gx|=APCk(97;@$B{8dqz)hz+ur*D=2=5;3JOL@iWc(I=a)<s#4Rj})B(RNJ3N@NDV'
    't3dbj{OC&@DXGz5`DrNU>VJ3lbqp4t$2>K^US@SS&SlSKUQ3(y2RX+j%qw3f<<6n6Q^)^v`}+f@hf&{@J8J_yIz+u|j?*)fbHLVz'
    'UFCs)Q8z5Fu%^r%eAhZb1!Mp9UR14(2fEW6RPa3}OF_R#;^e<*T3r&4f#-qEgZXS8^~~b;al~?2L6=3p1L`O3q%RH6Z$(+Y1N{Wf'
    'A=vIXEsyEPsAC&h+ew&<y}Db|Lv@j`rylR5pG;iM=IEkbjq*zKXxb3=qoTYW=7aqjvpMVF$wW=S1x+$d^F>n~oBB;L9gpt^&LH){'
    '32yh<`Pcu*OqG5A{d?uFrs4lyZRfvEnenm|3<P1ZIh8Jwm6>t#rKw39lQD2K-Ad0UM5jTbG|31qt=eKY<cSe9$`BKJ&rWL`RfprL'
    '&dCAi(X2#JY<BwrNJEF1b56+CnS*_6zk|U6Oi~X0<BpAaLqmof>B}V=SUlmH)<=cP*syy{qq-LE#6tuxc>^zGYS;@JYpggWF|0a^'
    'cN(dgjwo&IVmM&u*Klxv8Blq|guZ1u9(FrAV1hUZj_hdH4=`l0SRsJ@CSy@4X&Oh*UW|=}_hd%X&bCb*8MDL2)S?oxn^)d{47E~q'
    '*tAVY@3B!g@Vp<*@^4a7N9Er?1|=L(_c?p>aO@=}szyoCd)q*VXJgC$&L*d&iHg5{qXaa@#Gc+^x<zBc|1r?QZokRK!zGPJx~s~T'
    'CFJ>7kaEN(AMN;k(blPX$QBf<i^d%I`J2r*2J`ZH<Z6kE0stp?86+b#(h)D`(I%I)>1;CJ8!WcY+UxWpSQl@q0yqIh!Nvpk;Q{j^'
    'yk6@R%}40)v*A2oQ?4a7Ed1#-b~QNISj>~~W_A=)I?jcX#~X-~|G=eo=xj(~iGMWhZf{g|295HtvqeL;|C=SRFL~1gQn0~j=x;jC'
    'Vw;XoyBxVXOUIYd=nonlv0zP4jx6c4S<WV%qT`BiF^=YG5@1``E=LQp(TDi_Gf&l)n8did9y!K8i=!v0@wQoOU_l(ad?TO6J|&;Q'
    'WEXUv^3UWYeQ#NEJsHrTa3$j)Gw-2eXguGiiTEw)QCsl65M|Psn#c?>5u+UasLe;1xasrao2w+CG#Qu|rEV|A`_w?8AF%P<+~A~U'
    'RX#c*YQo}zv@oJgV?Aw+8PTjr;<6yFx<n_zPb%C9sd)$n`az*NPyme;$-lR?Qfr`D+fGJ4{77+0&)5O4$H+&1ZL#e{{smo=MCqSg'
    'HX(nq!Yg=oq|uo*YyR%yef|6G_oL)}kR=ft1J>5~Xx?nHS`7?ALl0SExPNo3VP`|5G=aC5AYYKz{cj1+w+)sEj<V%Ec4tmaq3}I^'
    'CT<lRU;MO<i)3+-N7c??SZWOQJw0nOKv?I5aSre5oJqhbBt??2hbwuO;QvQN_~fIoj=SIK7{z2%Ru$wNI+M<$8F4&TBA335_Kudk'
    'SxX`#k}+Y}EEALv9QDYGQK+Z@@XSA-@=7|^DwVN$V+|8sAk#!49j9Bnlp{Zw0>zqm(RpS?(;%l94Rwu*;P|?k0Z?1=0-&_0l<fo0'
    '|M~k#((!gO2<Lp9&RH><PxsTacJ#5@|JqD<|NCP*-F+<I_x}}qyl-i)PWxP6)+}dKAM=|TVEoSATTW$f1&dXu)=qPJ%wYF#b9+%+'
    'vZsDnZx-*_sGU07<(?)A1^uN}_cc4f>!5M6>%P&guS?zfXzkV88!M=;T&DpRqj^Hn*&SPvSGP`X5H9V_D70c%v&W|9#ufN~qvRUx'
    'r5CJmJq4fo?6PaBgMQ=!hywcE+gpQD5vO@|S0?6(!1wK?<(LI~Gb~un(6Cy=BmV7<n}HqlG_UTS?4TKT>+Mz7>1puUV%KqF*J-cq'
    'aUWQBgt<$BwHX@j*o@58aWyYg_UHU_U4v^BRL=6Ajy37hBM|*yn>r0%d-J}s#$M<-X2}Yca3%K&R(%-Ro5s<NdqsN#@7KWwbDANn'
    'E%r9{$_qTepQYOY>>*f09@rLcu#UYt{C6`v!CoS3)h>7VG%<?%1-scelC6FEj<`%FA+Bg<%St=iH7)8kd&h45J?=X1u{HQOTJ`s%'
    'Rcp^X%@651C+1h>bB&NkFoqkMA12iz;AB-3^9SONQ$ajMqk1Lo21D$T9Q}wZ$8JzLnxXa~zn?OXL10}~`Pv5m#62<|g*6b55BF9b'
    '_@&+-0-nEF&ib2GZ~U?975H6QO$Mi#biEbt<I|a-PvY8#T0ZBskB>LjVZj>KaMng_9d+z!{DO6eacy)1v+y9UH}0f)3x)<T5YCCg'
    'FeCWUAB1tQHt!xx4PX{vU+~i_JqR-s8~S=atVlaqHTVg8cqU@YdDra+&&PEg;Fq&l(~ez$WsiDCJAMZl^&VLd!=ieIv-$gG-RDE6'
    'J%qo%5&t>82l?>qGrU8uQ^&E6KrbC=72&ymkY0bV$NWX^x`FwK<>)^Dn+Ugvvplem`pe)J5Vu2&<(5Eo$T{a#IOhw%E&Rm82k}e3'
    'lW*vchx;bUasBiS#Q7Z6=_SsN!Cpi&^o13`1gqWU=g3BW4uF^AcipNz$YU($Vn3f)pR5Nsn1^HZh3R{^1K8`^yif$06a!68zy~<%'
    '<`wdPk17@Qb-u|5jU)UR45q0)!3Vi_4nKGAzsCCE{yNN<$x66$1M5+_mB~NL{tf!rZMY|X4<OE;k<s_yMgq8S?m<5bDzAnc=fiCv'
    'o=XbgY67^xV~FdA@1<NmJNw7);vM-6??;2lTkF;P*CqB3c<*U1)djdak7gmPa6ZE@t=&TzMX}dN$Gm|3RX!8Wzro%VNgeuad5t!Z'
    '!{oJH@1bt?QhCkq51L2P8Dp=q=Anamggjo9$WM4K=CF}lC5OHRpzo3Kw`Kfa!ZUmxc(A5N-gu5VA(1=D!DZk9E={=i@W)k$ON_}6'
    '^eucQq?kCm__ugJ-_wifK8P6phM*S=Pp`#apQgvt-;*}{{XzE=(%O4V^3fQdA`jpl&D=<d&Nj^9Ptex@kGA6ik2YS4(>eA7nb^RK'
    'qsWgW)<X0}-4W<pe=U98vCVpDQp`wpEhgY)@p4{sx1%-IB`1B<y@6P_0$ciMtsd9ksTaxC+Pi7ZUKw+)Ld?7J;r*2Vzw);MI#$H_'
    '8*QWF%WX1l^J1O&?5+R)7kG(5=Zw08m*OR{w?BCwr~=6S4b};9dAjznS6-`pls;pr+yY(-7O&+c-n(>Wu>KWutoPqwjm+(PE2Z;&'
    'nH&R*9o%XA41R9x4SgSIlQh{msW)(ckL|6{$NX84Ynnh#0SpJ^L$H3W>?fP69sdpAb&=m5<h!KCo88+qQ|}XW{E*E}q`Fhg70f%6'
    '$(?O5-M@l1a8bpX#GbM^L&}@{9e(WB%d6FN+>iMgT+R*P@i+WG=3s?bOP1pwG*9eqw(x#7UXP~`*M<EGFn3)eU!^RrV!)5{ezGDJ'
    'G7R$yk%z1&^nxM$_|N-svVS}7-df$k%Ygi2CmZLo#*h1tGxasuzxQ^O3pe6tTeDZMh1;zO;c7O)dokRB1l;(Evw8<E<}}Xfd-L6W'
    '`BjOSO=*E`TZvz5Q|egDxt!(G8{-rw^uxXy?>^Nzm9~PtqaPjj9=&+)fjic*R_8O{t~T-RK$)m3fR8l_I|2NN``Zl#@Tu+-?ummK'
    '2bPZOc<~xO{SDTt-<AJIi^+eKHzzxK`T1MT$8)d?h49g~IKBG(Qx96>2zF}m&K=W$ADi7V=pS(^uf1a?SZi1g1m_R^N;=Z~#kAMl'
    'NmV5G3d~nvy_)ZiDEF|B(`<{iD9wXd2K4|B=8JvDc>bElSz(<+|2B(d(2xIe`lC-I=lo~xAB<&IjMtz4@Q@>eGx)b6^sBxY{@O)<'
    'AfDarXescg7xDfD9(eT~jJ4y`vm;*)Bz!PLKj~}vfaY<aULJl(+(p_GKIVHkz%_$B2$!>!P#4oJ=k+=u=7+o3TdMV4OasS%{aGAi'
    '9yZpWN$`Nv10HZ+e-{)+f3R-<uDw%7`0h6=FyUwTdRa8V8NFo*S%m&~^Q6L-pSLhB5XQ5C!2Y8+GxzHtJs!TBbA47H-gu7wHL)#P'
    'M?GQq&5Erjatd<Sg1z29=B-7>KXy@DmH5WqX9fE>MS9k5=Umt;?PNE5N86#C3;h-Lt5t6xO$4;EfKDdnA-#lmu?FiG-5*#saPJOF'
    'eJe4G&sAQbLtsrc))%umOfB)gfk$4G^JGw|Mh+kLSuD?K;JJ7Z-afp}rQtardl$~_bQ6Z1v4%dah;k6}{6|g7?ZG^|hkf8vV^qq{'
    'bM>P#tEnFIJQ%Q}u+AUO={LB;f?M{qJpjIsm_MtFIZZg1y!Nv7#C}cx&&*g-J_yLLk2`BXoW$0M=b`{ktk<pKKOi3tvrS`9{q0+2'
    ';}%^I514b+WowA(K7ZjFu(k?&+WITfDb_P%ck5j0JSV0E=Mr->icjRk+{lk=0^AeUfbB^>jlb`wTk}qS<O0r3$YUQao|TuK8NX0L'
    'y(XaYfe3hW>_zTC|Bt`A!y7B04bla3QlId5-Q!Ph(*DL~4mJ<JHaGA2E4ok~$?0|ZWA+i_!RY(IvN2eX1aAy6f3EP-HH>#SuVU}v'
    '{I&61_ipD<UE>0MfbnbBLG`g=X97G!IUG&wS-Ho4qO*b}<X5KmyiUeXah}h(1TqYBM?fE+R3-32zQMwac?8z<9q=&PVu_4|9Mik?'
    '_vlgo)NNT>I)GhR0{i>}&M&N^FT<<P_z7>wv0aGu;2v9tfpe67&_BGpHd10EV4k;&IVi7_Wx08m`kwVbY{$28)QC_IW4U<b$9$oz'
    'Ut(U#9{XZokH*gAegA9I-1u-0PRHR+Kr>v=Gv_)fqupQiM3jh&R$`VT$nwTshYw~)0l(s!c)k+OM7W>pO));O>Fp=t#dl(S*bfKv'
    'A=J-@*|>2I|9Z^E1^pFd-Glt=g*dkrc;Zh^E>z6?oA}dsG%k((#SS>56njIvH~ol74g%`sKG^Ng>}yUvpJyA2!{@|BlY9rTM<4f9'
    '?Xb+;f2(2-<Fs$37@v*f6EbjjF+XgjYdAA+Iu`8}?JM+)Jn9p|UQubDNfNi0fJy$qm)iPNV!rKTTrj-I>2pkB931sm`^CNozc4zo'
    '(sli>>P9FR?6tCl)$kSC+67*Wec)k@oG|CHhd%7ntIoMMS%xmy<k&~3gMBch>UON+6Zz2^)+kOV_8w@Z&))hpOA2R$U~fd4fpgz?'
    'tg*X}@=Nrm;TI@>7kPs6w{X52*nGI2!~E{KN&Kg9ZsH!CRqN?IEbN=pnMmYiQQaBliIALl@O<n(-4)5hPdRyL^4bfk_j?rQIOB)a'
    '*<lWCE^hlgPKo$^ZH}zh3b9wUM)jWg@;_$!)WdPA3%P(bxO^VO-rJM`=Y4)J-1ci)1D>yhvL}8#UVQ;;YYF%Y?^)2dgGc4AhdqMV'
    'OmD=#a5sIr=d(9X&i;_)SC6Sx1L}G?ab#2H_Q~;yJdT+9nijA{M-%gt35Rg*F^0MEa5nOW_sJ34NtnO?sLmDs!j=!z+i19Fegtzr'
    '1KSn!t3A7m?(oM7ez4Xs0N!}2u90X0_mj6n{g&sevD|i?bBlgrtQVN1Jy-MW0iEYA7g%fsYqd=6W%twu=P#AWuI-G^tt<RHK2o^H'
    'kCsk8TUgt>_UIixZH+LNx5t(lv+;0`b?DaMc0D%2v=hG<(B@HpB+j`ZTHx$P$1Qc8#f`J;GJQOgI}bk(p53IiktKjLWVH(q$EcP#'
    'zYOlWIq1fxHRmDh1#n&Wd}48OOMBv;M_c}r;w*2YJ=T)4SVqOjfs3)}Bg<2HILG%M+=3k3Ui=cci7uDG=XVXZLCWa5$1eJ7b>@4r'
    'ux|NL-_y8cV65)S-r@4BvG*g5?e{JYNVe-NPp49R*zN*Zmh|C8oeFaj!2UbT0Dfm;UC7lNxQM8R+oAeeO${!rzrjV}nS0LXvU~P6'
    'V)z)BK0DYif1t;lFZg*c;~dq@c{kx_#A*Q0_6{D@!?>RubnK6L;!h$RRB~xSvUHWoQoQGmkLCzt>;m=rnQ_uNJ&+gTzk&~NAH8Gm'
    '@dEnU(6`5AL+=J1vb`pTlp7BA#)EP<Jj~Iynk2Itzwg~mxW-wDV5cv!t{M13mphw1{l#aK^;(CsNB8GSd^WpJ<nYVU!<V4P8fl`E'
    '9z_8?44zMHsH8`d(|(s80o7DQO3#N=5zqtUomi{nDx^o_bb}sQzX;b?9?of#p~uNuiRpp)Fc0ShNYTTRpoeOC)zBo)hyFx;uoOLP'
    'iSt1}D&>{q-loTej~C_DS|vRSIp^cV=|R0SRMI1<{kgc$Yuq;Dy|S$MaXt5rKEZj<D&CTpU-SupZ$EfGvCZVU4?(lwPTFg+Tr%}1'
    'Vj0+fnDxss+&#_)^fx_}0YwS8r6*!ix8Wu}`gnbV=d&>?s{ehW2KYuSrIygS5qHo1JM#8lcp~p4cmH<1A+dk!asPDw{<T~8(A7CR'
    'VNbe8_4b>5p4hTZFBan-dqzDR4;SFRC&s<wf3qLX!OF+|tvlx$_x2P1Cjssa3Eb<d&b?h<<lw%^WA42tbisVwcWb%l{&dzm9`;+^'
    '_X{%|r2fZS^tZT;gtcyu(jQ}`-lV-EUs6qH^MfZe>jL!-ngN>V0_3kB(|qmqIghm+&NjOp;BY^sT;u+-Gs(_2#NL}a^#H|uV4Sr+'
    '+py<f_GG)(XOcR$2FpW!^n4X)rqwd_^W$97l^(-h^jWLCWxU?YSp)04$NCICc)!HJPe22&wOh^#7Uq<o@10r^lWsGC_s2Lpth9A+'
    '>zJ&TMQ1t%+Qg6NC1>YO@R=Bt)3=8;@);_TzQ+7`F<qXCO@85@f`@$waF%Bcb1iW`(ddrf40E&0(z&jqcY00i4*Tj<Fb`=xt6k?*'
    'T;sunGa8Z%!kos(^VXW!W8uK{%m2&_6Zs>Y8oam9O21qqn*}AYCjW_=ue`GjYu$`+p4pz}IJWTp56mIk!~LNpv#O>z54LuPmseWU'
    'W%d&KcOLGadCkihqrsj#tSva^pELnKdNd!G4k%aWK-($CC&woP`_BAY=^wKK=0eyYuk1g7@0B~TQU1YmPahb!#Gc09xQXK!?)lZv'
    '`@#I@;BkB0Z!JHl_Z09y&i97(d|<nG_^th#VC!;}Uo;z2^DrOT(33boHimicte}4SM4bD(*2Nw|nfSJEH1=0Cz!u;u?3aW6L;M!z'
    'ny|U9x9{;rCZ=UQ5o_v)G)pCw@u<sq(RAF$I>C)MZbvvX<<~$fad{8?YVF;D9%Czh7H2Hs`76L3{D)>$v+we|4`-yM`PSFEz=`Kg'
    'M7)RJqqZ0I<ILjs61N(ICtL%@%OCFBnxl`nOea}M=p(`7bu%|}lqi;A78&i#JG^A_Tpf&Itl?gIR349t9-MocaYePpn8(HJezXGt'
    '&OMzl%Jk4IJ`vlyPlLFUPlFZ9Wy2aB?4$Ik9J)^f>m*MD|B3!?cWDq?D`^@Op2+FRp@GS1pvkPkc)|xJvxZo14VBl+gLo*-i#GZO'
    'UM>$TO`aEfPxN5C&x?N{4=|tZ<utJCt~3p(AIi&VFpT7Bfc+<}SJObZYtl4`p70Un+>1SV8ep!_>eV!;6z<3OuW3+uqQ~D|8l1RH'
    'mXJja%%O{3P6KCnKfZrSgA?^2d-=WCFr;aK`S;Gt@5Pgy(7=&6i%;2x_t(JXp$s2jZ<vy@vnas_IJe>T`jN@`z}!p71Ip)As3*&<'
    'q5iHvoO67C4W++a!%2aDaFkvH_NuF^;D=-lBDv7xISrN9>&uCbB9sdzt8s`ebvnD#6R&}ODyr5Xl1&kt2hb?IUSGDP^aP9bd3e~L'
    'pTmo>94|JQuRHc%PJ>ie6Y^q%YC`OXYYubPF!-A_G@i(7VSZ5L0qU1Ya|1{=9?6G(J4ZOni+nbNd3>U0QHk*Y%cloi@ce}a#;=Zd'
    'V~c0Gi1Edz=Ns{P4hM?!onu?@%%Ox_L|=A80S$bXo0=cr(^;>8p00ofMV6l{ydPN(iwYWG?L=KdXT^KLQE(3MZoW^0jJ`<qS<&lh'
    'KsjVmH0VB|ABfL^SZB8p_m9T8V;^ju%QzC%ZDG9280~2M^|<+m#lFIOIYv64(UtT=cu+2VKcVmFa=m5jt48^5KpUKAuCtmx=BM{4'
    'FRuN`Ysm36_ALl9y&LYWHDb1gS$ue{D;;MP>{*}od4zFE_#Mt`I`-=UUWV^)NAIi;p}suVeP7dZ$Y+e1EN9_S`zv02!5zjs<``GT'
    '(Z6H5^KiuUJJ1w!=CGdu)`%45MnkZ+WJbt?@-}vlJZ^II*$f1LJqmw;E`)Knt60%)hGS)^KYu^;?&R{(ecj~!+~a5ZK3%{*(=<H;'
    'a3)b-7@v02RvG()NYK*aeH9<>S#qmxGQyfL91#v@0^z}aD@V+~>;SGnh6NN~!`W>UTVwJ}h&$|od3-nzvSnkhADkIV@jcLQ+1kb$'
    'i>G4F0On?HZK|h6`G$F;cX6J7W@GL*e^lNBZbHoQSb?1Q&vZP**&S;?(h4&1=_|a^EXi)|mAMwMPBxF?KywyQ-co)m_JS#Ybf`Dr'
    '$Z$b_^~R$-T%DLKrrfs&^B=y)cCf%WZG>avfu`Yn(+uW-Cy(-ui`jnDd+hxU=YmGZ&nY*^%sC%TmLn20p2$VM-7AvC=0_ji#9LC`'
    'B<K_K2<}(d2ane-b7{+Rb2aL}^q^j4#SO!X?#6&{wvWMkAQzsPoqJtd4!EaT9Y_bfFF#x+>w#V;{QeUDx1Z9ziSplr?;Y>Z$mM-&'
    'd^S_`(cZMtXk*oeB@ce=XjtkFE??W%uUFaEqvhrQM@#Ga|55(;yEQHJf=bvO_rk6NzgzC*>$-pSdU5r6Q}BOR@ccy%e&@`Nq*+(i'
    ')A)to#q9p^w_VHqf6=}AzIBbS`t|-Rm#>|M;Qzz?|F?Sk_SikPop9ZD*6@2BUA|suSN}g<z1DNiSb_U&3QzQNyLVscAd^4msH0FV'
    'Jm@bioJZ5%`P=@x*GgyT=Bx|*3OyY63;Z`*$9sR?Is)vnj{W~YPA9b?*jpi#ScCS2uYEP0m<am=?<%;nFb8xAxWYA%j>6{pRhPfU'
    'H2)1}uA^?SbPK&3I^P|cjP(+%E}7+#KPZzkd{cnm!Nu!w<9PKtzIv@+y^gM4moA^bE?&JZbOwJT+b+*8y^gNFzsjCfAAZ(XuX|Uo'
    'U4bkzDGvL1?*P<MM(9fmW=1oZvYCGy?6G^L>ulXI>NxiM4D+(Kmc+WSFV&-ZbU&UOIOEt3UF1PH$M84Ji<nQ^XdfBqhh;pz+@TKW'
    'y<x6ZbxHG^$X>zziMGacv0HkFkauH>BSbII715@nyPo7yw)Z&pv<b<#JE>s2t<>Q<IOskH-^liUxsPj`?tBG4wSfGZ+I^X1CUY@L'
    'kLSgFKlA+9y}XZay>`s2*Vfg2v@ot-AFp1=*>jD*t*bls`n7#^=X!&yJNf$iwX5fUfp>jpyLV$+Hr69Hd0!IHaUa)jEzQ2K-xjcD'
    'ncXke>G7P$?^n8lK-Z`@M7qY`J+Ec{t?r^<y)Ity%GK-T`kL3Sc&T{L2cPtb?bca;ibrkGtM#m|)*oN3PtVuI7N_j`y%pYJ0)4VI'
    '%%@S^y3!|m`OkB%KX2~y_qg2L;o&0pH}G23|G)6?BFg94Yo1sazwqoA`F59w$&W(yY0l%lj@#p5#MW(Q_%YnT+O(_JSN~sbu6SX2'
    'y%$d)%e%Gf|7!w!QNZ8zYx-J(@87d87u*NwvV5M$<1<*Rg*65TZ#@5);w($N(<k;3Yr*{Jy8Z<Fhn?rSgWhCdZajSM-0Sk|dAsTt'
    '#_W<uee!m_g7pQu-#QUooW(O8=xeZvcC(xHGGMn&&=<nzRAWp5?KiA@Dp+Lid8EtU;Nt;{1EG$Gwf)^^`Yiw*68|IOA8WvPeFx~%'
    'B?IT8v-&iR&4(V(mtIX@&By(1Qj^E#lUETh2dYyL;<^z%Q4hX^&!Nu}by4y+@%3hWZJ-}-ntx!wG4oMh=*~BIcgW*fbH=;zGrc1K'
    'R_a&nQ{U+6xUJ8zZfsJ0_u&rhIPE=Km&apoG<zC-`>eOYI1I4v2XW7PsYlb>e%C9!VodVk*=~u?;apcWX8vIG0eh1L^7mo>)~4Rc'
    'eqp_Lx5zW$hR<2w&B_0#73`W`0-8i%<9uM<5SvenJ=gZ3zY_AZ_Dt_O#5c|{rha)FT36azJnfr}b&G);<NN~ZMapt9u;w%do(GwO'
    'v5davQC~>(b&R&>Iv)FTw(&yh3up`lyu{|5JselNy3^b%9sJAd>wCbtya(Lt*W=;U>)zGp8~faQc-*|wYr^H_{~OWO>%!IN!>iZp'
    'YrDp~!!I`G__CQe<ezz>UT+KMlGo$n8AV(Bw4CGlsHOcvHR>Z)Kp%EHyj2f-V@=10du)7}5v1>^7P{3q$5XLZ4EqJwkZ<kJv`(JY'
    '5?|gox8+9CM-*j7{CGUz|8w?IEU>Ll`MUc;`(k_FxuX+%iSl}#$8%cq?V&HavMyNf7k~V<KI#3fKIsVb$!mZ8m+xQOOV|GQ<yyeQ'
    '1)d}MC=W+n%0)3T77RKj&TU!lys;Ovyb8dFW0KwH294NuF!nuKy2gV1T$jCJo3U?%*vC8Pen@7|_^gk>qq;`iIHFEG9q+L|H=ef2'
    'sC%ZqPmC>3K_8vB?&=O1{51+s%p#0uZ`CFC6UfeeXFcyvJCs$}`+myT#^2{XX0Zkq>tRQ0(j7q-&y0EGjx{mvg31#$12_Dsu+C&|'
    ';+*xa)UYqKH*Sz#HY-%a8H+Q({eV4^7ZPh+VBYBCzU|iX(>0n{7rb+6&aQQF2h2930>)JRjkX8fZ0Q!xGfM8tqnP>w$B)_!mNV3-'
    'cSHf_3Y0%)m|xt&{u|g&n{=+#jODAW;Wg&|pbfP0H}lfvoWC5r#dJ0v?H8uGlv{i5&BgBLn|L`{=iCaMf23It_xh}cT$kU@$MZdl'
    'gSVG+oXd=JnvFhuuR(gK3q1B~{GHXSx0)b3Ms&a9{8)@n;Cw{5_pv{IJf(S};hM!SsAu>NeuI5*THZL<2D1q+W?nx$cN*;IHLpF-'
    '^t{GiwxF9#Fz(-uSpW1=IFI!8e5`{^>PPeQ%$R#?i<up0y?AY`f4H|PN3%&@f7v9r|A~Im@o*1%;tu=9yW2MJTaM=u`EE^f(R|P$'
    '{p~17WFPlYY_Z3KzbVn0aUP|Y)3=Rs@Uho={6x)a3uM|`d*^OPnSKNz*f@GjHqF+ib@HAcX#e0m44hd-vJZF|Y*3Jm)Q^JC@0@^q'
    'D%hAyn)LYR@wM_tLI?kC1o9mFxKJ;jPqfRZ9|p)*iqVYiJ<ofE`^eY2Vmx5osP=GuP%a+kDBpo@Ht&Js(JZVv>DtMRR*bjf9bd-#'
    'o}NMe9-N<LoRWPW=acs56y+nGjWXQB)H?;v2CKbr4V}lQhI>06o&;wl;&a0vjoWAQ<oH}I7wr6gI77cvp$#+~;XS+qIlkw4uLjLq'
    'ER5ppy^eH!HO=jsfaWpf{6F5yt%Y-6P3-N2y`$KCFJ>nl*&UDk-=~~1^dU{hdPuXB;h9tJ;{u)uv7Zc`*UaZ>&d@-|=Mp{v2RQQr'
    '&JN|};{F5R3;6t+`^nHh(bV{?1MH=f{VwJ!?z~nqlcKE8-`H!!A@J!M;ZMij&P#i6Hj$roxc7CkU)jD^H1F?bZf#cnS-cK?{iyy~'
    'fbZaahH^KixcW**f9*T>3B|uC4@}#$yH+>Q$HLB?j<N7RF36DC25fLP3u84m&}RqtB*60usV=y`d2X?{cnkeZpko?Kjp>he$u9t3'
    '4~T~k$m^85N`5$wH_BTXVIII5boGODZ2gia$)<bUPj$DCXLL9JKk4JidhB5hfcE0P<Y)LRF?`C4QMLa_2w#7uZdwFCPbMXOR4Kn='
    'pa{OGk1OmSf4ZvnpGSYz^DVOL>iEx&B;W_?;CE|c_;>~s^zmiz2NLkH@17d|J6YoW$IsM?3*n3RuUSvoY6AEx3HVRsvIyae`Cqr5'
    'n0qdQZ`UN?2MXa2B;d!7&z=&(7t<eWqV-4l&#pI)cY3)ddVhh>y)&N3)xR@?C8=|46b0}j?my5J!7s_de>hiI0N*@{;iF&l;aN-~'
    '_$M)Zn#&X`f*(o1KVj{YBKWZc{OF08wg|o^0bhT@M<s%<OTaHYG3Q$Z-w?yMuwKAW2LEQygTzMVdDyY}crWv~ce3y0re@`N!1NhK'
    '_CzGqClUS={m_K)2V(f$C;ILP;K!DD|EN!$6xlPeCEmY=x$=teA4~9`PV=5s!H>l7$)BMJzEGcx>HKM`_Ak^YW8(i<kv$m;^~sp>'
    'o>b|xvCy7I_^~?tcg6JAY<2#eSVGsv8W6ne73sQGNerK6Tr1LbdPfQPx;kC6C(?CwHrKtO3VtMp-_sxO%OQjxOTahO>AF2l0)A1Q'
    't<%#b;Fq3=af#p?V))pnTp9ig67Ww?%(xf97uos+)|W<=uc23x*nf=nz8d($qXc|Sovk+%$v=bVu$>gak0jtnPs|Gw!H*^2YwG0h'
    'P?LbKtMhdXbus(~_H|RWe?tO(>6skBJovWb3+#NC^@4V+*UoxoJ?V9k{)sud7}HQ=e-2Ax+?$aq*<%M43EX4fsD%pL8zS2qa35Pw'
    '^xMtHy(=O2uwGb=-fQR1I8W-08jtrs5a8afN#H(KhI<K_hkg4hB{jHrC2&7{e2%sV_mL3y8s!lv@wvH0G46Y@D&MjltcAFzo)3<%'
    '0`~=xzY*tRQJ-%m^4>p*b#0teSy6-gSmaa3UK@+Yed;3IM`GM}pP1P$z`Z76=OE6DYH&Xk;~x7nKH5K6fP0aj5o^<|C*}+Ya9<GP'
    '9^;t}HF{3G5aS+eM%3t-1yPIz=WbJvKP9+d93^nCESB1>H^jK7p3SBT+!rk|-(!5?s3yL#h{d?4{=~5w-1j7K?>=5<CcwQtkidPc'
    'DpzP>NZ`Jt%CFR|`$F8?)Jx1&g8Qym&%wCPQB7QTQ4-_6N4>R_;NGc7;2!5jD7kA(d3G)DcXd*y=dAPW+9Jyx!`vN3GRMiYYnQyw'
    'F6M41v1?0tc5SBDn4);<S{LKqqIjAb+`D4jV-J)1Pz~-QG4820L5aLy7bS3yeg#D`XDxwy|MA(|`M5v9^CaMdZRaSsZ^U%hD39j#'
    'cTFs+NlD;SO~61Ae2M*c>(BJA$%ii?^Du|#q#!3g7S*H>{D5jQj>`7Gl7Js8(eYzZO$vvv(_8~Z`0tA7k9${B6A+7PQd0PV5?^vG'
    's!7SfSCPXRi)vE3*?AzU_P-Ls*Se09nwVHrlfvQaboVQQZ`UN?#|q(#>5nxbkuvxz3HWMiQW<;+`rB%3%{V_#e93)#!^dYv<mx>l'
    'y$gGmRLI_WxR*o@e7hzKzo$g!r@3Rf{=GB&hv%x~;~(y|wE%vD!>_1-ALZUXBVLb+_NJP%ALZUX34CQ|@6L?SOZZric~o=v=GF<7'
    'n9bKasj>MiQJqi%|Cw3tBKW!le9WIcDuQoFz&F(74iWr<1pML?b4^6>i(>egyQm^}li-&m;A?7f2NAw?lz@-9a|K24PXhQ9*HV)^'
    'Pw*oF{G^wap$vYm{u8Ei|CIQh@cxZ03HU?QffT{-Nx*m2<ggL^p%^~;yX%%B_^trH%k)1bem{ioOThOP(tjZVf1!~7*Anp8kN0{M'
    'z_*3^KgM?}YGPdkKS%#h=K*6**H96BQv$xP5WXdV@3LO5fhzp>B;Yqx*}njPC<R|hE+xTtCE%~|4pIc)7sIFgbyf6VNWfP~|Fr~s'
    'Q`!A%=f(O{_?DWOC&6z>z(@Z}MG<^c3jV{r{Dkl&<RALqVpZ@Z<R9uEs?NV7A^%YSP^5p^j)eRJ{R4R5xmgn{>}QX2A<uI&rZnrm'
    'zvO-yoC_1r$0yBAdx;iVe@g7#T>u-&7_B=KJD9dcYxo?S$BA=oHhY{=ZvcGV8|d+DlC!5^bneevuc-2A=Jf?RQJ+25D_cdMGffcF'
    'PT^x+yfXNa5I)8fj;i42#B|R4$J(q&5&VG!d^Is$4nMCiK||+t`G%U>Fr3*{F(lwq{;DGQ1qt{?HFYWkzbJr@J=9BTdLR+}k{EtN'
    'Q4cVL-#E&_SCPX>@K0j+*n?`Q3VtL3KUU-0C-|`hd_{dh2)-r(UsvN>CiuD>d}aJ+h~ZOT5LNpxh~Z;j2o<rNo}dS03O`oJe<Jy('
    'v%Uzb<iB~8fFCJ@f0BS-RCoWIkpz6~3!v!!H)An;mG_^i$-(cb!oMy7|D;a;G7Sm%)Q3|M{DK7hSWRD&o*=fHg|7_%67moGa#)J?'
    'Z%N2M>OreW{#z3A&s2E-<i&Oy29NEY)ZPD9ECF9rcm6C*3?J#Q>i)5G3HbP<DS~fEz}MB}77_e{1pI=!`^PFuz*kg1*%S0dOyE-w'
    ';-VV(d3_O6_$PJv&+Chr!jIMAzb7I8(Ec<P>0dnw`G@wOs{6MmA^)s`Li|g}Kg?}xD3X6Y3HgV)jjHVbo`n4C>1z5C_5^(qQ~0QV'
    'se&&d|FAFR!~UoI*>4+~(|L5q_Me>jbn)dpJUcT3(Av8bJDwT#j>UsYF^m0_KXG>8omp@>u`F-MdegYytonnobfcut#_iBwrG9oj'
    'Cx1J#_&ks96SY&b?Fi>_M`ya`^?Nj9o-_H(y?U6B^_4d<(|A^Hj5x3<N8Wa@Hq?9_ULy&-)*tV)bOW!N1YQeI^pU-R*P#SnG4{NE'
    '8D4X0eNwzqzW?B5cr8fa)p(*m_6@u)B=Aak9WTRcP7UK3uUO0QGQ7G+F<vXr=(k_-8Z;#EI(#Kw4QnNZ*W<%8Jip>Kmf%<PT_0bE'
    'S8Fe`PpU(F-9BaHUHsB>8OX>x%(d#hjDKY0-7~!fZs1i$-kn~HR~dQNP?AH);ID=7Sq|kw4g9zwhL1Uvfhzb73HU&Rx+46?rUZOb'
    'NiSFi-;#i@re6|+-;;pvDygAh@FnD0y{8cWt_1v{O87GO7xoZ{)$|a6{R-?b>>q;t;;cv!{DBbuNl`Cq27e_1KTy@fz&wiVHH1%n'
    '64li4=H>gH;j78FWbh^EuV@YwgD<8(&h>q1zGqesp<4F5S_YCsF7v;{3pKU$^@SL|V=B3a8T_>be5@x@w0}pW2Vs9^)PshK;5Q`T'
    'yQ*qg0KO@PkF`{4YUu#JB>~@5*Gt0bNx)w}ZeI!E55@2UOCfw$0=}<iCIZ3t#qeY7UFj==zYxN=5w4nAnkcuIN&??8Rn@XYR#1_E'
    'zW}(3_Am60A#77sEgir&#qhC~N)`VHmKc8AP{;p4PXhi>RV_Eb9}3~)`Li8W@LdV`iu!dEd|wP7&%d(sw~&CZhW;$>kSBjU&VSg?'
    'p`r+WLju09&JUQYe<kr(>?P4t1wYphVTZkAw@$rWRrJml#w`>06t`Tdf}dCSWn$dF$a?Bnit;{k<ERPzlDfRxym@#8A7RJp@-B1Z'
    'o!Gnn$m5-g>Mn*w0el`8v>uELe%HZ<D&+PJ3g+DBZ>jTn=jvJs{Drc<g?1pZf1C+ZSLJhENWgcM%)w&t*Anm-O8Pb;{BB;~ngo7q'
    'D$%tVd<p)eUip?H_!9g_cYRM0d`kkp8eap0-xI>OX$`924<+DR%FbUmuWwBXf2d6U<<6%`;iJD(75*0z@E6MDZ?`U%e_#(_?<h6!'
    'or(l}OIggl>og?b50&_u8GKU$zOSTj7K3j|z+WrzwK4c2`G<CPLs`tX>kK8}Tgq(h+*vg#eE0F(Ng;e+0{&Vd{ug5S*f&j4kDJ_i'
    'H7R^c$$T>2w>;n0*L!Sc1m+ynRM^^$+?am~KTy?Ur*V|of48n=ZUw?W<@!1p{0Qfk*sAs~0iWg;sDYn1H{uK*`y54T_AdcHwiNQe'
    'J&=H}W(GKeFXn&jaitFbkp%o$N$-Aw-xbjx&K{nBRrK!;gz#gUL%vcZe+2ut9h!@)ivLa``A_hH|GTQ>?@A1xW|6DHf4;A|z-#Oa'
    '%4+PLydFOZ{N71fk0&Ru$4?4hS61WeGzt>%i^^&&okmd%A9LLm)mS@uJ$_R7v9cOZC$Gm(3SU>&W5&tr@sq+gl=T>MOo{W4u^v+q'
    '|L67CA@~N1^{A3RrY->=>2D~4Z%Dv5a8|M+_yr00MRn)jEQ;Y{k0n#p{!0?@vB#Gp`D+~|;473r)=2`sp>Y3^1pJb+9&1iskDUZQ'
    '&dP4+ir`DgKkRX%O8!_9^3T-O$zMxC{-OS9s^UKh`G-AbOjY=okbhRBkp2?#4|~k0x_^2S@{f9qD!PAq67mmwyfjqpUqb#_>Uu0W'
    'Jqh{O!+aM_5qt^x(?k95s0hA<{GlE*iq2n8LjK_VyrClfyC)%k(Ee1^W6tSG$e*D?{ck8Ce}<8|`+q1Qe})R>?@&ViP_CgO`VS@K'
    '&ydcbBKQ*e7v(xCI{!nF{420rKUMno(2#&{sFQ!fTuX#sKps>CzbFB}gg!_`@JnL&G(T1meD^2;UsKlO)p1V}@C|kPzZ*%w$NNu_'
    '{^`bI_~?J_DbjyjO#*(b&j061$iJa7`_m3YIVe8wi>4$8$`HjLyBPDSzw2t^Pp(Mz6`Ai<O`So0&zU)|wHqp_HN*Uq{GKxje5!X='
    '1iv8xf1xV>?3CYghQoK1_1rn-_nb-Kn@Z-kG59?R_{!=ZPWe4&68Omf6-Dq}3HZLM{5yc}OTfpuxvI|JLJS}0W(KPGPeT3$$bU-m'
    'FHhq73tnriDF07ff3aY56YFb5@FnCQ&P`U6e}59!Uo2R!0mo7VUqb%GJtcFK8GH%(gY_?p<gd8?0pTxH<=>vf^$&FStI9t<iR&L0'
    'to|lY#D7jj0=}uL{^TUCf8e#wfhzc>1pJ}8^XFI+@E6MTUvd4zg6eOqSQY%C1bkDO{vob^Sg;<)jw1Qv_!97ah4^1cz+bD<|H0P1'
    'Cx0yX!MVv5)@w!${sDeN0KdU{eW|H`L|b11zM8q^48A1+-&Li51N@!@d|%c53-E^$@YhP_wlnyy7(UiNI;!~3mw<07r2j$!eox`~'
    'TT8%St2=*AMGT+p--aUi67mo2Use3)NXS33e|<&p#qy8!{8dGNk^I9xcdjb^C#Too89w#83RJ;&CEzbq^<T*8HJE`<{#RA>7s)^C'
    '8}GNO2>x0E{#r?|S%M#k<lm6%KZ@?3pdp5jJ=X(8_zz48_(N5(ubf_kS@^!X^B43a;4f79Uvql>W#GpRb^1@>OTbqa|H$d}mxVu6'
    'cmD)y3HZJ`{X3SBKiGdKwiLk^%OBQ%M-l#GQvyETfr|Jqwj|*9RQ3M>_&o{ut}6dCz#mG$_tl-h*p-04R;T~OV)>`A{|~@lNWeE0'
    'p8vH3{GO`#b7a>m67XGR_rG12kbe&HzoiJig#4rUw=($m`>#as6SA2rG^bHX{*kHO?f;R1Zv$La@bC8D$il}TRqzKA@Z-m4j|$;S'
    '(4S_X4iv!`)BlA1A5_8b)+FHLY&k{v?~3Vv0{%ZKqW}Hbw^{hu17@HIzQq2!_4lZ&YX4&Xk8tLbGWd}Md}Y0^O<h9%VgC_LP5%*q'
    'FQ$J)GnZ8DUrhfP;A)nt{YMh;17-487s@~E{Z)T_maq{1Kmva7_>5=)e8ZC1e^(v-4NJWLnED^7+W$%deymLX8$$U9u;~m$YT(;q'
    '`p4?}?*V)<{WZLQRPmp^l7O$Q|DI{sV)|<!e-!n<GYtv(hqER$Rr{Bae;W0FQ$zoPg#6R3y0Y_MkdS}6!uzivA^&t+*{lzMA4$Lu'
    'RQ10z3lj2ACmyURf-gaToOx-hf-j&y)n8!`K2`7|3HX7k{*z`wB>xb;jrNx!{u9YRgx__P*}p|gynmee8{4Yji}%m;&qxt`G5<6B'
    'N7eo#3HX7MnbQQ{7Slhr)%l-_wwV5?e@3>d{Y%il>!|8K3-HDCXZoii{+Ez{q<<>9e~S|G5A{z~^1mb@|1^@ns^E+FuUqQ;-z5q8'
    'L;9DZ^IwvXKRVf<iuNxde^CEY<^L(=${*}M?U4LY<$o;Y${z+F<&UcKU&@s~3H(@@|DlvCe>i;Ne<kp(qb0F_l0gGS@WuN_`&W_w'
    '!#Y|k3HZwFU+ZXz`Je1xHS*s&+G6_aBm))g-xkq7p#B?*^ndFplz+iHn?a&#|B)Cz`TrH|Unu_&zN3!*T?zVA{9TFuX`L*I{i}<='
    'TPI7rf3$xU-9OgJT1mi<Rq0>W$rAJbiE=O$!MDZqr}(#``}ZUv{~}A-{1Je^l7Jtm@;?E5G5s<A87aE|P7?Ajq8uz$@FnO^F%UKQ'
    'k0j(D`kzk9;149=2deyU0AI}iv8{6d0{%ze1KJ;o&R-;wf8_f>94NxSNd6&w^1sy-!57dU&K|;5l>Y?qBMJEG^v_5n{}4XS|63`7'
    'KahZr`iC0+i!F)$qyJ6O`HL;_{!#x^6n_KwD+&04s{A{EA4$NEmFYjREv7%tzf_ce0Pw~1k8EY}Pk_IYfFCQ<zhepcNAveo@n4?&'
    'vztAHsZk6@(f;$~ABV52o4;pimU#cVtxo=Fmc;&v|5l3Nuf*_)|5WWi62Nzu|4Whl$*sRg;iC^k75sq&e0BCuZv909-&Qt%)5@*C'
    'Na3rqzqPIe{kzKY|17O5ra$UGit3Ln-Kt5zkCp9Tw<Pv&tJA-9OU(Z#(tlOK7xRCluKvi<CFEaZsk47|3HitTPm1s_A^$Y8KUCpA'
    'l7Nr)uOj?Q$Ult#Dx<%I{L|?EQA2-2LjGywgHQ!uV*eO_QFQ+q!t>ALkE-Ac<u8waDbjxpq5Ng>ucIRVH-z#pssB_(e=+{C{!>%M'
    '|8^t+Us?T?Wpry2@YTsbqbosw%s*13e-|wA{v&ny-&VmA?>{0RSWOXpG5<$+{uSw81qt~>`Ok{<&w_;fXZ4?o=r1AvV)B2gf-k0j'
    'O#a765qt^yQ~sqQ{*#b@3iF?>f`t4-{Zmo>lU0<Ef0%!*D*vY_A^$X6UH)BBLjGwA<zG=k{^{fcQX~J067o+c9H@dXra$ICs)H}4'
    'zfLs}is&zte=Pp2?EDMmU#znKkX01QznJ{Ls`CFzmc;&Tb@pG$lGwkktp5$bUy0!>%zrCcV*Xc||5&nX67bc@zmhGczry}QR>@vT'
    'zz-C{m!QA8`a7#6A^#$RtLXeo$iIkua7y6!j+V^+mF1uHjw1PIGyj_+{P&I``DX{b{#zCNNC^K#H6S%L@I~?ubN{+3;fv|7sk{Gs'
    'M_WvP%~n=_**n^i1pHW4{Y&rI71N*m@3x}-cg6JA)x}?XCriA4U7i1<cM{6KB>z(xe0|x;odePzvKhQXRdWb5%W3T0l^74yi(;S%'
    '4+8kS4~L>Sc<&^-2M9jOVMTl(x(5h;tjZ4VokaHl??a+W4?5Xm`m=j@r3k*5{tE4Y-l<!YfUm3$zjx}2>3<>~RD=J>lGwkxI{02>'
    'iT59=>x0ybB;;SDt`9^nl8}E9`JolzUqb#xREwf${}S?#;&96LFQz~112j+sUrc|j!&0S(MiTNbww1-9dy$0vi@VD5AbYWd{L|FM'
    'VSBNJ{85+(){7<N57~i=_%D`_Kh%dv(fNxd<d3GV4x<-K$RE}RQx*Or3HX6BJ2aM%KU4>*ivK0#k52MW&HgnB`J>zF_OD6kU%I+F'
    'z@D%UrOWC-G-dnG<Nr~Q)u5=mfAi~568M3tJj7mp9ZCW}R;K^w*P(Fu3h$r%I+O&yvOZ|N{5lj4zpJbcpqF2V!r*I`IzMoJ9ZCW}'
    'Q052DuR}@T$I9X$`E@89KKfxTRr`-5;K$1JZ(TzEQ5~u(`b)?^o%}D6BKRu__>MCBQy0oVcK@o<KXjq|b5!=B?&(7L$Lb&z<>B=V'
    'OJe`jheQ>8iTzVA@RcI?D+&0Hsy-w=!xHm9n**kX{|&n)0bki1h@N4K>5p{~s^UL}EvElTVH_6ruSK26{4lpw_-qf>V&eadj#G)@'
    'M<3NIr*2@vPvi6>t{l5T<!FZ5$2e-g&)@n-KYsu082hEWX&$CV^TQpNg6X7R>TLd>_O5O@bzMon%RGT?VAsjTTx1a-P}mf~!pL{A'
    'Sp)bdD>EU0Ts7}Ll1#E<Im_KR^sY0tb3qZs#-G(vw_2_KSs&KB-tn=2Q^b8+ge&h5-7l@j;O2E2^bS*Boi)z)-W~5C@P+(1MEG3<'
    'z9VtFMEE@fepk_e20uO`@O!g_9f|NyFutqap&-IX%zsyo|G*}~FA(^hSu&@>w-ESp{>>dSe7~t4>yo*5gL6G>l6urqzh?-1SK`J*'
    '_#A;hr>X}p@nZzO_5~rr-vIck7W1vDiA;o_BJkDtlhk9D`@35NKL5*2#zgo71b$3a4_@Mr5%}p}uD>C|cR_qDf9|OIKS$upkI#tk'
    '83KPU=N}dQIRanRq^H7<5%@~}&57_g2>g_6{h8gt@=x-<<Uu0&<KH6iT{`~r2MBz%{u1$@KStnh==je^$Uk4szk+D~`;h$8Yp;9<'
    'PK3`8_<9W{!siHlCdZ$O{t^qaL%ii<rLlwbKs#)4&PPULhw6cL*y8MmN`=1w@d@MM*wO7H@X7KKv!jdYKUqCYc0|noljjrmUm)<w'
    '&H>rcLyW&iNPiD8{&e*y+0lc?U(n@)Vn;~+dFOguRP=}BpXXDagR>(f|2+R34@QH3auNNfiw9#T7twzm6W1rg-@*7g7Ggn!56^$)'
    '2S}6;gPpuS0-r1ng`K<w0-r1%kexhu{B62?xa@?Gf4Uw8k^DU&<exnwt4GRC2>EC0dayL~7ohx0bUqLw{hJ9;{w2T4oFG*AI~boX'
    'A2}1C{7cGw97OBC@DSrqxBp?ngUA2mlAVJy;q4Ik1)2O49z6bp`6!u~^%3}F`KXzgA;#Y$^Fw3>LjIlT@}aT<lz)ZRe~Id0u>zET'
    'h1P$G;xJeN%D>{AkC+JGL(pHx0us?5l)r`6e~ID{SmEsu_zBtiTX^|kkKh576OL{U2n2pYCj(}PIY5^alNFE*)_#z8RIw1uf@HA9'
    'C-cQ-mW$}WM-~gmEJy~Qb1@L*WM*J2&|5ABA{zi03#9E22~|xn2F3!Nb1_iqpkOS}ITr&N|9SBEpY%Hr&A%C9{PiA~X#OGOpU%ZV'
    'B!6v${L?wfiPk?GA^*ynynQ149Ri=MCKa<0@=p-1zcxbti5Z;@+D6E~Lf56E>i-UbPnMIN*$DZka#0ji^B*Dq3PSzUM##THufa6*'
    'cM$xqb0HA%pM&6kofDkM2JayFzsw0vM1KVT6XpbG4ubz}k1Q7#a}fNm_FqJ?aLhsQzphD1#Q)7TS+e(7cq;yHu8ESp$D&j1KbmWj'
    'Wbd))1r@#r_uq2Ka$&LNnkd<OEILt6a@JgvBzunqKa$}K1U^|TDr>GulD)@*3o?9o{@E^BO$63lljIGbEEf;!BIJ*@{}IW*=9(ng'
    '@0!3w^1lnpzcLn`C>IFpg7U{N?Qb3x{sMttkl8=F9%B6Ia&oh-2ao@0Mo9k|JpMw<U@H6t0-vlVEbF<5{(E$1Ks^`He~-=wv4@a<'
    'Wlg*t5k5Ts1)&d64<Y{wx|-Omhme1TOO^|l^$_x}&~XS<{fEb2+kdF&kC1-_T`mfKMDU;5{}9z=;70`i>0G2#_z3<hbCD9!AHjb*'
    '7ne(g50Agj#YMya{D|Pc(g&IdAHjcm|3!umkH5D65%K>C!T+}Q!=mZ`3BiA5E-)&5i2kJyEYbNNKY{#L`oI$HzxfH|zoe`QMI`@D'
    'Apa#=|0L4C`DwO5;FI}ZaN#2QuVa7~MEG$33#|iC;qMUmWHq6<aN+r1cw{wUx$yc3{DLYM8y5)qXSrm#D7iq$KZ`CGFc%2<XVLi|'
    'a)FS4wmyF$ntzb|(`V0jWb?0p<e$bTJOAZ{3-|w|W6-GZcL;p4T2Q>n2V1!I`TV_T@BhdbW*)HNF}|N1)_L|C3fp=du{~e?I7Xu^'
    ';W|%2ub2kmA>P^hsPmw{tvJt;pMm!hF6=`*S_*mJA%1fA>hCDXtZ86dk?d#qq~62(^|<n~SlD^g8Si5!>&kxaW&cz8T%mK7jj}>M'
    '>zDdpxSB}3;cM8p4^htc?n2=WUt=fCB=%wL^s@L#J+mQSN#Zg0Zd2w<X`8Rd8JOd=jqiVms1rU%dAwhbw%IiB)bFxrblRTpIfOeq'
    '`+5K4S^ie`PrmQyMm(;bGufZEblb{Lu?}oGE|ce<>ba}sYbbv+4IU2M*=Os%o<lu7x1PLXy!&WRv7gnubH_Wx`GbDn>1zGF9&PsF'
    'YWo~_9&~@?T<IvRD4(l-Kdpl!g1#yrOUryTj%<&zzrvuq=gxK;KRu}N{Uz^Dd46+vEP2A2t{x;ECX$xR^s&sF@rU=C?_EDE^He1|'
    'R~tp14#!P4f6UV%uM2m1UZcqBMX5F7kNHAX9>3G_?$(|q^X@EhY4SzN=l(fgpd5!}$jX|9w^aGc9Jd&N<M19Yx}#bvz;RGHOA9#;'
    'Hqkf~@HnWPb!2(_<T%U`_&RqS5k3R)b>29d`k4}+Bk<>hd=Mk>d3!kx;%^Z6DsNUygrCCrzQQHR+vRwF%p3U;U+1nQ!XF^;=Tvz^'
    'CH@$J&j|bPBJep?-dc%2N8pp?jg$D0{EKzoHrJ;be-7e%S|_9Ge~iGN6XI_W_*~_#Bf?J+_%T)9Jje5I5%{V45aADCe6<fui1;7W'
    'zhW)_sq`<;cM<q%pGG8q{W$_(&VQe3{xJmpM)3d<J|zD(Drc(fKNbE4flrn<UE-$*e3du&mIgn$h4GdCmk`bWWPrd|^rzy#7=h2I'
    '^7hL9j}iEsWc`u*?~{9npnu|$@PCPq=zl_^|CabJ0$=HXDG~l0fuAZH1Q9-i@rwaT-tZD1A^(dp;rvJNe=#Q<f5iGzsQJ%`@Db}z'
    '!AbH~YkVKE{uD|E63ss!A^%j}hGIj656eGoe@lqwpYI~@=Op@1i9bi+tGwYv^WSF(d>Z>-i4V&^ZU6F#)<1;)qw5xs(SL)$SNkt2'
    '`I92>If?yG<0JHMsiV@Ze+d0s*G))>=6|F9J2~4wHYEF>65oaK)&7T!{&NIAq5hLF1pb_E{ZBXopOfrAOZ*stujc>}{sw`csyRS}'
    'p91)2`%6Kje-*a~{5eV8vJ!uQz-J`(zY>3pz>n$l|H4J!Z%FK~CH@@7*XNH!^S@vS`~jW*Rd58pt{q5(A0zNxC4-3YHwb*G|C8Y('
    '<e$$;&R-OM^ZEB1zUBcUe1!bd>rYICkC1=bAB~Fs2>F+c$=2WI^Y1r&b^gkU@DcJaQRhzsB7B7WOEx6_PbEG={uQ@`{YS{ZVnAkp'
    'Xg>d*yxU)?^#A7b@5#IUm5l#<g#1%=YyAxoK0^K#O8+C0zdl0#>AJN<>yHo1KTp+7yrY_b41qr;@qaAwIRf7$@qaAwV+1}Yv%fT-'
    'zrW$DJqXqKrwII%O#f^?e?Q|B`GJ@C0|Y*!TYr-=0zamczln>$-?XnA?AY6%!Ht*(lPt=gpTmW{e_Sb_`G@Uvwa%iEcZh;zF%7(5'
    'VKA5PmZ`WD75|c`*p~+X_|Ec9`NT6ZOI)j^fBc@WG8L1w3xnQ&KL%_c1)0z>Bn!KE91Vqfr*o{1>{lk=Q^o2mC9PyXf>RcE9u841'
    '-~TNpX0$x=)x?s0dX@LcJ`K~ixR^3Nz|Nx8kC&*EW#P)*hxbeI81$Z0oQkAP9*u_b@5%OY<>|N@?kwdy*oWvT-9L_&FDecwavrww'
    'IotSt@*MRo;l0JWG}B7aNz;gcR);VTpJo3PZPIgJ<nKfIes(7e9#Y-Mz{}*g?jxtyn+7-e+kH`Id5lK#d86z#9Q|vr;>ft_vwW9n'
    '@GR%e^5tjH-N$|V$mQHn@lxj)uis<j+=%ermCxpKTzW-3$^<{pcZDhcm%h_Eu=IU;Tvy>Xx?id|DHVGq$0f`(zjS_Nyd%d<{tiJ`'
    'dzK8k?dbZiEKF{*SuoFLek{LPwe8Q1cJp=a4=#INz@g{uCjmcB{4AaLX-9sXYCB6R?O@QUwui}dvCQ2*>xF$4Pqy58yK0*+{v3zn'
    '*=5YM%9-6ZX7t1R$nQ;2ZKuL$JLdf#-(P-r!+y0rtG0XY!umi%`R%)vHupFC=69&j^eAb#Gp=WiZ8-)X-#Og<IWN)&8td9bZDY=)'
    'oD-$|8}_6uR56E1DCHx6nv^mj$Rsa+<b&>hz4~#GJiL>#?0=+85fS1Yb^NUO>O9Eul1`PjV~lgJI<CvD*$x-gww%kAw%a%6!KgM5'
    's_kHITpv__U*TnS|JZ1|#=P2C#=JnR5$q&oSm*1qtlr;QQ0)&-#sEFWCZE_wf13G5@`cH}TvW%HSI2PY?wZG(@1QYl(&yGXuCcTy'
    'w$x{Z(I2CKt|6OT;JPWxpy%-&^gM$;ceh5H8?w=u<98dQJvQ#2!}LwQ5HBUFYtzU6c|zs)t6rZis@G@6b<eoYh4H*ywH;R0juz{^'
    'AMcIzxG>gl%ea0ruLCkd>N;af#Rp$UMhqHd#H=O*Hlk4mNPWB79t%?jKs;WT<E9K~lp)&?S|<Q~$NOTA%qqRMTSF$A?Oo&bsy?UM'
    '7I41}Jr5cWLuU0%`f*{lYx)*KMx^ay`kG~Muhs_Ui#gxCK5+j6dY(y-vB`4~Po01<6tIkNr5-WpTw_nfEBdo+8+#g_kIn0b3>;?F'
    '_W1O14$h2qOv!Ci4x4hes=KJRA(wM*v_JM?qt?ZJMgOe4qi!bvja6;{N#k+nZ<52!x}5A|wLJ&!XVCMmE%z&HZ7Ej(IjnLO`R(g9'
    '8|&<`VNQ09eW{wGqS~J1#&ySN8_yqi&3!kows*!peD_gKl{{g6l@9?q%uC;%wz2(&95%<-kfY{xb1%@X?bl4*)6`{ax~qAeHD4di'
    '0Xu-PfAiCmxgVN>`wg!BhgzQ>imDyq<65oTi)P)ZwjUVrX1)*HFUk$*`6kUbcC#%7BZmit{5V&U!*_A>95eUSBerj}Z<)5Ey4=jc'
    '{+n{Nd5>tyS*hPO?+JP18PMAtX6?^FaAy$dG#JX~rTfRH<;!Cr<@v%+_-eA#HspJChLWXW(6c_+uJ_^UK}5oq*zy^pn^c`+@W9@M'
    'tFg8*bLVC+pDnn<N?US}y@vP8Vtqg9$!8q2y-ej$%d?lMKd{T(Jo0y|`I~+ES^YK&hP|kxa+}@cVV)(3wd<tw951e7E3>QZZQZT{'
    '>cAGj=M2y%KwD9>Eey7y)@?^1-;b4!E3U)$K>up=xNYqJCvwkdv&-aa%{F=A`_{(;I#=nG=T(E=Rp?uLzYRc-8ol?I?yF56nVGh-'
    'UGqM+K4y>(ZjMO|$W`T6<F=3O5&v#>mCJsA>HA)8XNb?fTb#z$Ypk=TzFV`+?f|<$;5ME=)Oj3|8PNHJsn6DBGD1ek&%9_UBji5E'
    'KJboQhn?lC%8x1Uk!!5H-nUL}{<06H{`1%e*4m=1Y0)-MpjYs&+nkf}+}FAFz21Cby=mMlZO^eD<MzJR=6+N_{Mg*~`WKx$*RFfD'
    'v#PndcQE7uN6?40&xK^}CHqFZCSNaHv+L)l=HBRZp-#AMw0(cFH!|0h`kM1+Suz{y{LE#2y4^MO_H7QFd5h*VZ#kzH%{CQq&fN`w'
    'Ikz#_By-Fhz$Q{O$jz>ln_Vd@d$WXD*RhjwfTuX1CvJ}BoUEOP0B5kKovXIL_T6Th*WWRR>`pL^2g(-RHcxHocNKWsI3GI7H{@q9'
    '6mtKqa!>E#e69A%Ta|};?F?VxcNq)$KK7T#JK)-mS#8fR9^dBc+w`*MZFkV~YW_;idZU!P=KY|IDr?C6L(V6g_a*Av^dYezT?<}k'
    '6BTni_}-Vb*q13AuPfj=ta5w1{l8}p*YpI@L}QZ%RlkwCpHl65jpm{0lX&Mg@6}9wJ236)44%U}ZmVtm1Um~yS@Ib4GF`u*tSRy4'
    'r&}4D(l=ZAN8c#FUyBFFy}R<P>1t>zUu<QIEyo|66RI|l<u3jqeiw^oKCAh@iDtg#0zu!q_O;)D^WZK(zayagZ=27PhuLNHHh(|3'
    '@O{m_g`&4*!Mcy@sF;YBdRX!}Qoi!uHoABBVSXc~tEH-~vR(JjwOz^>1{K%vqWpa$C(PyjQg?gEqI_-3dyjE`^Cb1SeHqhXKXZw7'
    '_Scv9o+Lj`bZkT1Ssvrj=~>4?thUE6=oRvBgk1STJmC9Tko~Oc!i1y2e(hv0QU5GsIumOe4EFK;TA$^}_e~KrS2|})8`O=X>`qZf'
    '#lU2iq}N-$96MHLMyrqUCprd1j?Kfb-{(MfqGKQ&$$$At-Zy;WLG~)&bssvzG?e2Y`yln_9}4@mjDeVBs%B4kuVQR6C;Tv;`u`ot'
    'g9|&2pO#N=u`B9)Opf!jj&%u^-MA0)`d4aa82i+Y*#^#^KJkOKn)gICKT}{2W%{w+&71dypzna`_j(KRfv4wxOIww5^D1?Mld1*u'
    'DCbx_8Wyp$l-HL+$HeT)dQ0n-;_adJJElj@-Js+ly%y)?`Q&<ZW5;<`$a#~jC6BM=9Mk8W<?mE|9>hM~?J2*pZ~JCj`zAxonJ?sW'
    '{@z#Y5jv!bQE6RY@&CQ=ZnORKDtluckDM@KUyuhW2Pf+9!!%I!+LmG+EMMOIF;va5bL}>@R+qKu<l3m>pt!R+`+6vOI((9AdKNv+'
    'Kg1j=nH#D)bb3u!|5xjEBz2Kk$~F}XDRmO-@vL*L)tbMs&o$(9%%}6wPvjEckn<e1bsg50YqMNSPx5`NsPnLudefG7hPI?(_7=;f'
    ';&vj(vm!^*Gam}&OB2I;16%D4X8rHILCd{C2VP&9^M$k0@AVZUn{=(7^m~16xxUUI*`;bX-?gt_`Yk7{liRd+Q}rhmeSNt`h^y!@'
    'fd6Str}!i$)4I?{81&srf%xeo;6vMOqH}q+4bWK4V_)iu;tH_^)%X7--es6KU!UyE*a0AZrUyN5YQ#M@$3a$Q$7itzGvA1(Y0TT3'
    'F`ctj?{zl+kQgs0R-8k=SZ1tvuR)*aNqs`aiQDo+69-z08y-Nh6qh}3G`=u4!#oq;Ce3H)+YHDnVIk<N^tI#PL|?!spmt83LwPZ3'
    'vEu^pR}|OxV?fZj+dhBLmt&cGz<Mq&Ti<IwXEnJoYi`%~=k<6RSnle0qpSG5)?!U+KDcH)jA=*pFO(a1=JRfweaLEjUgLW+zf3Lv'
    'Or4KF-QnaaA2IQ*1Gm<J7ch;LkAS!Mrg3W;??4(0Mcdip+gAFyt@MKP^^%?{PnLBZxnTO{oBB`9FB9@p>zemB`_6viAH8VyTQhUh'
    '%z*e`bFFk?`dXUC{eQxqtsXCK?Adnab+;Bzj-Y38mH7I)jIFiP+PV$-`Gt#%{Qf?P4@v<WCWmq??3;P4F+S$3->R6AdFR{a+t%hg'
    'C=fL6NZMN0@i!hf$8*=#892`cUtHqH^@*=wEl!MGIL^)YWA+rKU7Zo+iTK1$-N@(ld_+*boloL2FPi7|d28-Tj6KCC`FnslEY!S}'
    '`(QzlucsPU7#sA6^|x`|%-^#Ga*m#iwo|h|isn3Q9I#KCzxRy1a3QePdBv|n@7qZH0uV7JJ0NGNFyny09HvG)-J7vTfPN=w-kclc'
    'vUuj~J>Ir;t)zea`J0QNFK=H9>-&6j-(2tYjm9cJs7n!JS=m#S`FyM|+KJ8lIi@VC>D|eNIgV=fF|RpJ7Tm|_c<tnu?R}pix3cZX'
    'c`X2aLdB}99DrBacK|lt+F1_Ye{GDQoJhv~aL%Nf?IPSYwShR{^BmSb)-7#kQGU~z2HS0X|09d?>@|dWM){0g%T|{IXK9%^e$DYy'
    '&|Y2ToCjjzYd!=upMmV6yjq{-WCwYMSt_^gzh~}kV~px~#4fY1s&8|T(s*Y6$(Z&p;~5oO?-uQOhC4$m4AzJEDLt$u{rT!4lk2W{'
    'Ts>#!Gn@DS{anbg-nD;zlrKAPu@~#rk5oPP>_d4qjB_l{A<iG3Rjm!~EK6HQ?x~#p@;8&7qT{78M8DtfrjXa4!p`zl`GAH()$i!N'
    'NZLKc&P`gaOVhhH_FmOZ(J?;v%l$e2NcA;~pGrOV11%IkUg$^s`#q=5<XJ!aUh?+SgDvH$^%z{8mb*t)AE#5sC`lSVuXQ}+&1=+o'
    'D09TAd~>SyLO#E8|CZe_@a%J}P)WnxmFHrfrJ<_-BJ4DBJX_b#xp&Wg)S<+*|3FWB{a^E6|M?&P`+wKLo$d'
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
        print('Official city index already present. No files changed.')
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
    backup = backup_parent / ('EK_code_backup_official_city_index_' + datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
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
    print('This adds a separate, dated, read-only index of public official-city sitemap links.')
    print('This installs code and sitemap index data; it does not change the database, media, migrations, routes or JS.')
    print('Stop the Django server first. A backup of replaced files will be created in your user folder.')
    answer = input('Type APPLY OFFICIAL INDEX to continue, or press Enter to cancel: ').strip()
    if answer != 'APPLY OFFICIAL INDEX':
        print('Cancelled. No files changed.')
        return
    try:
        apply(Path.cwd(), Path.home())
    except Exception as exc:
        print('STOPPED:', exc)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
