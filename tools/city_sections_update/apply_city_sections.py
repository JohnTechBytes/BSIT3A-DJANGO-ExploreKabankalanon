#!/usr/bin/env python3
"""Add section links and sourced city profile; does not change databases."""
import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import tempfile
from datetime import datetime
import zlib

FILES = {'templates/info/city_information.html': (('4b280087cd9b9da62b5bcbf169bae6d7f58d94ab36027be8bc78e30845522b25',
                                           'bcde7c8decbaaad9dabfe7bf0ca98ab882ae6fe25a60f714472673cf6ad7fe5c',
                                           'b791b428776ab18f268febb035a52f377fd870b17151fb84a78fa4fff1bf7a17'),
                                          '2ffedecb659539f7b55fef33e42794217a344bae925d5d7e34c12002a1ffe271')}

PREREQUISITES = {'apps/info/views.py': '745d8f2b24e7b2260ceceae3f236a130fa4d7b7c6af972224dad5e3839e80d37'}

PAYLOAD = json.loads(zlib.decompress(base64.b85decode(
    'c-qZeTa%(%ll?E}wIk+JEb9~#F%RVpu?5Q;x0eZpDg^<Z_6ig8-)CiRKv1i1=bVV|p`)u5Hhbq@xpHOhr2hAh!+W#~7l-%#zx?=P'
    '`!Cl&B>zo6eTx<ce;fbD`VfVG{O2F<$$aHl>zZRWH*WIkd&)Xon)8#}H~gg%29`8fyVCr)=uZyIwz?WvwXbx~QjynAyOnxMueLC?'
    ';&VH?oNQ^o@|3W)ROa}+-dR|arrHgUP9!HwldhMKs`j;^c8w=jxt!d{7~1Awy^Id)rP4d{oG_n!tlP2eNZz~~a)4`7%sKq9^qr^7'
    '5027H7D+3h=M7DI-pj#Nda*NYg^Q%VSy+0oY&fACZw}cy@tpl(5y^EoYKHIAdTpT?2gllns$v`+Ww2jL`Zu+0$nBUu%YN_c-xgNu'
    '1NJ#C==rnDT2=JDZRzRTbdWmjdb*Ipv+B3DSX=ZqRRgShxAg15QfiW|YiiJ(@iqO)3HP3s@g!Wv<Cme-{qn>0$7HL?hb_rR5A*ce'
    'WCNOCc(kQU-GSZJc(QfOdN{1hz8m$9PP@7Fl=@!v^J~AeKE*jL8<Wrt^Lug6{P*?>dw#+k6RR;<JJMyhj2IJ@G1M;hufN%=-Dc=C'
    '1}8UZz1fn!b7*Z!Z~wz*0Kb^$huzRqOX@}RJX+J6LeJZ;Fy}q(i`NhLj-|scM(w&cgFgq;5{@Mun37XqC>)xTwHxh^H12@*d8+<!'
    'Z!qU{VR}cap*LOFa5-gs>=$MexEX}YPR+;X%_Uu@7@-HBTHtdhsQEMwzFWh00=4Z0ZbLg^ZD;se;!K<Ld(7)<*s>P9CVJ4lXdU~o'
    'FfV)0(#ZzwTW(Uj0AIAO5IBJ!%K_tbyra*u-&<$f^g_(D_HJH6_M`FkMa*sfrR~28Kf`nH{ps~ceq&2v4L*}Prk*{w^{1*#c5b5u'
    'U)Vf5(ItHE5C-snyWYV3&ZF2%Z0i-*d26?`eRBIN{9K2fz1=d{CVId1q;_6cS~@t>y_nMqxI8)i&C$j4oN0YyTZ3=I$oMuicPGyp'
    '9389h=VLY}?7MRsS}kC1zQVO@*gsk(bzZaDZW14eby<37HzqsyWvVLO)qBz+o`B7J%~2E{$;a``2>bOkN?O2c7{iajH^#wDcLDjb'
    'W2v+T@^4@(j2Hd!v)-BT{9&(+Lt~`dCf2&rW)6Q2+a|zDG75U<ckt*Ez5zcA^qD4UsawOdeB0E&kw19A+sM~0TF~>gVDl&Q1u!x4'
    '^+;2Uz?sqW;j{7h02@6!v+afKh%qAKo1x`}z~t8JY$dG&+xI8odw&eRG{A=g!rN&X?2foL#65Cp?<;=rkSjmMNAGqIuwU%wn4=N!'
    'Gh=OK&vskpWS_7D-;cmM%#+}nU>l6gK{!%0>5)C0j#krBt!xii#BMkpV5(pHs<wf333H3YbAJ*8z^xp3mUi%>5WYOvBYxl+a@}J-'
    'nLld{V6;!q3^!_9YueHL$xiL^HHW3-L|A8S6zF$2{sg1<_VMdAU_ExMG2t?`vG%2MJ|LDPjuak;*5m{qO0vC{f5B(ZZX`$GjZp3H'
    'SNV9OU@kF6+pqbUu+?M(yT$plM&ffHxY+>r@H_c@hvAM^*JeiayK|yzy#C;n&Fu;J-8ucqb`-dETl&?#Z6(-?-IDY{V}SYHa1?z;'
    '9L3+&5u5Ae`@}PZ!TQo{rlWWex{9&(+N)$peje4=@9ouj*y%;Czu94(F*xlx_wB1a)f(ILSN9)lccPGR2OCeoU6+(>QR0%zh<Q>y'
    '3;rCeZRrrhe)VNEepb_NqM2$kntg|7u6tDYnlo#Kx-`H1K9+RY3tS#=2(R#=LAq?H&#ofxNZ+^t*#@{Z*Et`hTFiL5&LL=pwlq(!'
    '+@<f{$>(P4vxp_oJcuO)&jzpOzhS-)eE$6F<NZ5u$3yJA(taF>OBUu6Y>C*~em$!c3$kZ|%Xf~n#xuJ|J(&Ntk1b$NM=}_%z-kK3'
    'xPG7QfX#42enS6)OTwi^{ztI|w&)uN#DZt&u`}XE?Q2Kf6HdtYzjj{tn&~88r<+_eTy%k%>w1DUujjXMpg23HVI*R&3N3Oj^B?RY'
    '{SChMSLe4|n(mE85t<!iHx}lkwt#&Q<0+08T0{%9j3;D&5h1p;>(Rm*Ka2bUaXO&6_kxAwCCdi#g3dP36cyuin}2D}lD>BP6jz_h'
    '_{(BOH=9!tyMvK3zQFhIv<&$S=0O@dEOEzW7}!;u#^pSa@%cYkPqK^*U^L5zKEbm6bN<b|mUERoGeSqveax*!IS6zTxJ!n<<uyN('
    'PI0UO&%3zBqPz=p61oz;>ZFM8&)FJ(FJ4+Y>EJ-%_m^$=x-<=7yt}Q&TKh>ujQKhhy6o4ur!M^buky$DVse1k3*3H8VYA?TD)N^2'
    'L2kRM<UQ9MoW2V#2ip5m{(gf6<Y(qsRuS_FyVsms<s9h^c?URx^sA^xq&2_LzOc6&z4&h{@OPW8U0vQbY>U;DY|$7TGOQr)$9MU4'
    '{nsxOa3`K6L1V45S`6ij8?}2_!&i?BskgVyrxos}yf4#>$WNj%@?nQ+39z3*IdnQC`*fbZ(%5R}!q0uUUdaIW>09K+2gHu;QlfQx'
    'oTJ)Vj+f=j$N|pCmHEDB#)TpCnqAmQ%*CbL*hkI_|DMZg42=zpE;74ibAc{s)xCDB_HMO8uAM+TLF4(V(p)2-!+l+h;j9rO==(oO'
    '2a9XgAFgFkEob$?&p|vf^>Crcd-5+_JIltZ+E4N73)-(QUtf1V)@2QL_Oy<BMQ%RNZP0Jkk<;&7X&pi{GER$olhPXcTz82O(?jHl'
    '*au@{0gEozzG^SP{Mmzk_xj=4nbrIS;y%?iVB@0=KEgbC?f6}?%}brGd2c}LNyeV?YR8;>@V&r!x&E*)ZLU4=92i@Jy4Rl&1`1nx'
    '=HLLH_us<I_MP*|j*S}l_gG-9Ei)eYcYF^Ut=WF7Esg!MjCxWTD-Uxf;12%29-0?mlWQ%HYkvLGJwbuTwW_QW$F#B6S6lLYd-BCI'
    'jpTjWI>EoN?-#m1bb7L|8T^;*0q)zYZIAIcVy+247FGX>^J`1C3$A|3aqm3DJdt;-#T=jfw@u}DuFYlp{$fun^`o8R-{TV6_rX49'
    '^|wA^K>Ic3d8RwIsU=nI#Wkm*RtLLa4XRYsGFXGS?Rw}%f{!Md-w%_P;#lxk3w}d;KKpmD^`ktGxf5f#WNYM<M(u{*3Y!C`N87Ub'
    'XBwNv&H2h|^y-MS@J~7U%n#j8bC%bsgyub@RFCs$AK)`fuI)hc^Bh|@T!wixUhjO5=T%@DTr6GIZbJiSUiZi|;qR6PK7%GPy9dMw'
    '#D@zoG4bEw>zPgR>kh*IfP*BDFO!}3D7F;-_f)xuuMeJH-1eh*WHcRf0IZX}^?}jbtR{71FzFgI*!TPvT(+7IEO)*?ud%RE{vE}x'
    '1oxi7Gd0_EBE<7DcOJQx4EsXY5Z6~~zgcX;7-HVp|I9s)*8sdL-6E#uSfF_B#v#?j>*ND(v)T$ghxuHJ&&qsB9DDmc;z%`C^bb@k'
    'J5deVl60y&)jkks-~&_#Bz@(J=Wh1=e-u(|;Bm;0#r-8bN*w!-;8eud%f>OCwP#*xBY#k>hx^3!na^^3G4`%Bugrfgtxq2DMbe^}'
    '2)~~sd?wN$E};8cCvXydSA+f6%U<QXGh)Mj!L{)516xd9khdYm_i)WF#Qeng(+mH<Fpc!V91D)h{PiqiNGs<@!B=btgX%jwVCT9f'
    '9>XE-$#@Mu_@jH;KlVQ{)=ivOF3|0RW?B1iUD0|ykS(&GkL9>q#QXMle6olm#B1XMqu2XZ$@gO^<wjIH;`0gi!@IGq1LeWu=UDKY'
    '&_5ISS4g?V)7w-%XrvWNYZ1J2rfY@2-p;MBLzh2Q?pbi2uD>j4ZyOV6qPonO&YvHJq|MV0*mD_qwMGAOhE7X>Bd*z~5${=Zs1$qW'
    '(-^=;3T=I?%mHx<_>rogU6AM6pX_V6DKtd8ti>2Z8D2{mYBxpAUYv7O*3R+V8Xz|4R5y9BugGJg`~9rwKP6jhJlT3?-G`6w;B!JJ'
    'm+)HoNBS4}yxSNAnYPX5-GnWTgB>-ge)GXGmuye^z7I_v(;gJh!@8)J#or_6>2bXR;{j*8=ADiBUn@Twf?qzg2hDA(rOoP`tjV7J'
    'VFsPp(JDT1#nG$4kl;naBh{^Uc^!c9hgkaP-YS=Gj;;cZQ{)fa4}T47Ik!Bp<tMR1ht`38+G=G^cjF37o<HB;Dz{bb1bvlbXZ8q>'
    'bT47@#?JS6hg}LD$m~<>Q$$));3)eHyjPmf%k|9QVcbV<KB-`VxajRSG~g_Hq55_WI+t|YW4#oYV^)0xZB>akk2O}SiJY^FOU79x'
    'U##v?|JUbV-M`k|+%k;hYb4!LTYzKjhLO0evs<KH>CEq__LyT3w`DpDONx24sn$a|w#<A_c>(x&OWZ;=Pe+pJzG9s6oP@@_q?{+*'
    '_@$vxJz-9<4C`*5@VrNQE7xU+=`Ya8z<NTq9Y1)^gFLe82QP%tN3{aGIP<N>#^2E9UvGG4{qTA51iHQ8f8SFmRvPQ&&H4Gy<|k^<'
    '>|icy;3V6JL5j7n@9}l7z5d2|Qe7*+UOiXpIH3%jPz;8>+FVEZmmTAG@WY$g+b=oS%liUa<7|x8z}KGi*`_&4OF7^7`M#{TnUe}0'
    ';m_{wE9*Jv`tgH(rhbv)yZhXCeAVr&k+U9+h500EB!<kr64f|eJd?j0Mna3LotjL&0ylf}11=QW<+f%4ENtv}^FTY+DF%w?mh{%W'
    'w);s<C~~aQb@zP~LyOMaMcqx*9)E65pJ_nRr_>bMx1Gmt<ce*X^wn)Frd;`s7w^XDU-rv}M|DriCkoDaH;r1Q-uP*3`z*G8C+3y$'
    'dxO<-U4Z!bK}_J<X#U+NJoE{69-IYyj-N;MaM)1jvQpja{D?msD-7A!DbJn{-V9^BGP>)Y+U0z`tesx4hh=U2z5W3oadK15IZ8G6'
    'Yi^I2(eoF4Zn1)%<UXR-qr4s1*=nDx<#An~^5Yl(ZPVqL<Rae|y?74t0_X_pG3iezenqhHLG5`v>W?G+W>3#6<hnJ))r=dsUIXnA'
    'QvD3v+Dhr1$L4bbZ|iV;>`AaGVHNg&TFn~35B7}md6)XDxbN;l7y)0`G1i>oImKv!<!N5eTVZb455(P^>j>u$Ys$$v!xzQ@cNgc&'
    'To({Eq;_!@aLX5u>SG>q?MmK(cx=>YU2gjH;x-KK1$mz}MZHy_^MZkd{JfFzaLhK2ng`M~ly@OFp>w$AO`dgr+f>gL7FeTAxsX&p'
    'Q(q9(M+)8Mw?+>0nzourdO&MOj(~kQ3m%6~DfRLVTws)ZZyp)3sK3ckriaE0B?QN`&U8Kn8__j_cT8<H1|MRa)6jo?(t-`vWKf@8'
    '$?jpzP4e2jz9k)==`z+@;`8;IYEN{o`)<m~u-$@vus7N7nVs@6D6U{VXK^kWWB>ZVspMck^qr0T*_9}#(@7UHKb3SLo#pLdBjjk>'
    '@h+br8waKOYqYL;{Z=~iUrxY413AfV*=`=;t0(RO>>F5%M*Ws&(pqjJC-$t{9L?Ml^*W9^YE!SjTt>4^V~DYq=GlJ>iATo5{)#wf'
    'f`(nY+<U>ApqhJe4pQK$lp9P!J{Rt5U*4`g5?{t;jY7R!;0Zj3xYRFt4^uje%W+wa0f;Ns!aVG#p0hB!D^UjnhRj|(G<zw0TCvT`'
    'p7x9IGN$?ya_^;te@SZ!pJLvy&H9OQ4?54IJ+Z6vI;vgdbV?7pjdB(0Ar<qTOX1NoFDHk3sirq|$ac$c`r#V*r*n$+-8mbrwSUFc'
    ')3)tko}Go#OSs>(+dD3!ko+$t{~G%Aok8b~S6sAdT}{RqokhcE(yU%Vy)p@(Nh<JH#7PfpSNp`DUV`<ek76p-O-ttxTdzMkyXp2c'
    'l#JsrF7sy-m~p9I_-!$jtF^|UIi=W?t&OmPxzbtpl}lI`-#nkRL*8HV6a1t?N7SIfn`M7nDDuha{5)RrS_0y2n$4Hb&@g7o{u(t!'
    'zSrjXz<Ha%$YuYYU5oF0>}5>*iZNjGdA7HMFsps0g)N}FvVERWy^6FDaMA*%62@hA-s(w&f$)HPw)r}-{{yeDt-x>KEYA1R>-j^N'
    'iawJA&4>7j&Mv>PKIms>`Ife)pJ^`32JuxdDCVbtTPatKjf8w1_@TYpL2CqAj&rQW&(?<W&YUaR?!rbb&-Cgpw7TY>R~m8$J>5U%'
    '55Ki@*#||gY2#iS_syc0quN;|;H6*UJjZ-GG9HnaLwl@;)H{>N4chNvt>SyZw6LN21@VF2JK(*2WZS<1t9{3mW9n62^hs}B`L9v~'
    '?!SJSN<G5TH{gq~K=z^7NLqyJ0i`&3yC0;hDR!yU?||nvGY%R6uQC4D;iJeOdbz)}Z7W=R#7#=?fOs5dvG2$|KHN9UX90}aoIfdc'
    '0E;#L-51|+?Csc1J$XuX*v+*_)4-NexJRrHiOUMDa<kqyrCa2%i#|BFuRRYF8M><3DETRJzd<}~(0Vtgs*UurZHsut`pOzZa}c(@'
    'kU7t4ZQo~qL(HOg4$NN7nf)fuV9ka&2N+D}<PX_+S4|3=@|j2izJ}HcPlbl<Qa=#Yap^ng%`P-YmWKcX4Pdgy{T&MNiHun4fbVOo'
    'X^fm`%KkYb{kBBD<@!&e{v+k}pFu*kUOW?8VL}=&9cFnq#-@4)p5045>NS^;d(wL&SFO^ZK0B^iDcH}5>j)G>CC8+E{GapXVn1$t'
    '`D)jjy5QfTTO#Oqa4UQ${jLTM?=`8~(`&@36q9Y}-LXZ!Ehj=RUg+~w?Pz4jHNPt(^_m$ERO2kiDEMA?2Ti$IX=!&){kvL_<sH@r'
    '+PN7l`v&D6@OQe`TfajeY42ZOH|gf8t^2JLICu?BQS|&EHXN3gL1#96Mh2`?9g?`<jk!VUoq&%yVj%S7rMS;f;EU5=^7peVbupeS'
    '4dd2!D2cppVUorX8gSSEA4?kMc(wa5?LKLpab26u&syh|dr}B<wD<F#-YVNq*j2m>bz6@dO4mIu)rGJ89$c>b8@A{@wtW^8Grfvj'
    'CFdaIfj`izbDke*b0s{x+_Tr3@w-CQUt#JgbYC5NLi|g)QO@gY+N1Kbmy*5Gg6?_PSv9pRcesro)Q3RN<9B<Yk)Q`t&(atll#k^('
    'S@!uVJGb6bE!bloy6iYlRb=E)m%Ofy+yyZn`R%Xxv<nS9jJ%WQH_wZ9_O6{2QXZ6zOE~a?p;X2_@{!JKO`mn^*yA(3<3{?5G23g+'
    '#zjuXG0iV9KF#N7q<=&F)(CSRatiKE_)h#bN}NUY5z^m;WAdLVae#@rna#pi#**P<+#~ghxYW;T?nt}uIX`KWhAW<%VeLK#fxpEz'
    '=OE|R1lMye+s<?(=gkM$Q{E#VqCOR}Po4TD|1tevyFP<z`57nYy&C(9E&r-NZVc+ZJT0y7>nelwCu{0}-XSe`(Yoqs*5B>cS=5jS'
    'Q&bxW51Gyt@wfl0e9pMUbMyfI?29uL;#=-vWFH33z-MZn4<^+6N$*`g$PG8#hY4Tg{ck^EzbQwN4^-QLR*#|cX|C`+e*cN${W&{J'
    'tYdGW8A7U0rFqW8c_{Qa_Uj+SL$OB{j&`!SSMwO2*N*a>qArsD^>}UcF`rmx?ONq-@NW#hX-pCib0GVDKb}`}pz^)~AB1yS>#_9y'
    'BEFkI8yUx&{C}@@sqbHguaCuCx)aQ|2j4JAvq+>HbN{{G_ou%a=vOV@C!IS9^W0Fp>uDTB-k<fq^~<%Z-p-9%qUJ&GJ~IEmCR(Rk'
    'qkI)SpLlJmNxfv+S+BeCfNOPG4GFodj{MQs6W{W<RFjaXw+VX%jFG=UkI*}~*k5PoMm4exVwypEGSh_T73a4(uhG3R#e34n^xkW4'
    'Pnrfgmvtv;X6pBF+y7V|F{ha0Hpn)UEFM+$r1t<r*YkqEj?q~}{ZjmX5AX#aSLVOOX~g@C0mV4E)W5;;RSp)UfvJWka*G=cDe{B-'
    '-Tdo5%=i3mu@Z8975mm8J;L<_;iGAem7GiYyKZmqSgX}c=>>Rp?$2N06KgzsM&~@9Li&_>pqe9be;Z>pg4Wn)n(gYRN(i5r)VXE~'
    'Tu@DZ$#v6z3=<>jbAv7pEvof5T6@khBqPjgMfvxXr-|={Ui(?iQJk0kQVkz5DT}S8_?T<5o4zvmSc1KZw2Bt<EYa7Karohm!}GjL'
    'f)7(|G=}z0<iPgjkz;uu6+4A;$L4ooD0ZEXi?|gReMK7w9M_}#gL(%={VXyXx3$o*#JS^!`U8KW=jerE9mYKi-)r8!`@bgMbjV*3'
    'Bj?<k^Rlwz4RA^CFHMd#wo4jI0nR&*^(yB-%;5qr**h&2yiDjUZnpb5n*^dJkd1>iXXA_b_W3+0@3yFZOL4SLwVE``hpCngZYCd)'
    '{rBlhZ5X_ss1ISBwA$wMm40W9H7dQ|Rd9jAdW`#(*oUOb`&CsQ%d|yBE8l;1+kbY|3k~Be{=Ua&w#;Lyd|jh7KRL7Rshn$Dk{nsp'
    '{6Ew-`o}CX=o~w>YQU%@bT`@ERhlI%f=9tySa(CzMcIe_a$Zb&tjYnZ_`4+hj%*Da*?WG!>)ou{?K)rX`8gvGZ32^9+cfsebR`X|'
    'z5XRlRrs2yeNb)ruJ*xapU*$A$=<4EXJvJ{@^>$gUvs~;Q5v7)w0JIK<va6BxW)qwTJjC%42m6;L(=&Y{Oo{y{-n2`&O<tLu0a!r'
    'o5Q@;UD0QP8%ytUnxq}P9p$`Kv*Z3cao$Co7T8ux)L|<*LiYaR?Am8i?tKIQKR(C4o}XvuyK`t#{@VqsJl~`KWGBm??#_@qzgDjr'
    'N}_jy>KblG7X6O1>fb6EM7@LCIlzV!>d(E<-)hi<Rb310H0KNvtNPG>VS4|*R^BVfJi<KpYq8HgW#{wM$9R5gi2l#FdF43~)p<rz'
    'b|x0oi*t$U9J?!ipAA}#-V4I_BLDWG_xKs=XLAdvmW;6_&I>X>;Q2`x(uGH8EpWnsdYjk7bbQp>boQ@zprf6kp|{iyJ`?YzkiN*z'
    '$)CADFguT-@$mERJu>Ls;p_X%3fEDgWvT8kr}Mrn#<sRL@XlOehKUO9pgs=FbtCjKX>6yQJKgoAJm`!2q_?z*I7N8O&O@@=m#R!o'
    'q?5T1KtWzjd=*bZQP-T%-w`;nf43i;*_1T+g5G%~?aH}9p+T=2yN~N6q4DzdVDI={#y9c4<IUfG+5Xob|M&l41x1J'
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
        print('City section navigation already present. No files changed.')
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
    backup = backup_parent / ('EK_code_backup_city_sections_' + datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
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
    print('This adds Attraction, Event / Festival and About Kabankalan section links.')
    print('The sourced About Kabankalan profile is included; the duplicate site navigation row is removed.')
    print('It changes one template only; no database, media, migrations, routes or JS files are changed.')
    print('Stop the Django server first. A backup of replaced files will be created in your user folder.')
    answer = input('Type APPLY CITY SECTIONS to continue, or press Enter to cancel: ').strip()
    if answer != 'APPLY CITY SECTIONS':
        print('Cancelled. No files changed.')
        return
    try:
        apply(Path.cwd(), Path.home())
    except Exception as exc:
        print('STOPPED:', exc)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
