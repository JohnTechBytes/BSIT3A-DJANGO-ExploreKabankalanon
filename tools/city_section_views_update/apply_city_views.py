#!/usr/bin/env python3
"""Install separate City Information sections without changing data."""
import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import tempfile
from datetime import datetime
import zlib

FILES = {'apps/info/views.py': (('745d8f2b24e7b2260ceceae3f236a130fa4d7b7c6af972224dad5e3839e80d37',),
                        'ae7d3ae21ded26227a533c8ddd97218414bd4a407de7a6c00dded11eccaaaa81'),
 'templates/info/city_information.html': (('4b280087cd9b9da62b5bcbf169bae6d7f58d94ab36027be8bc78e30845522b25',
                                           'bcde7c8decbaaad9dabfe7bf0ca98ab882ae6fe25a60f714472673cf6ad7fe5c',
                                           'b791b428776ab18f268febb035a52f377fd870b17151fb84a78fa4fff1bf7a17',
                                           '2ffedecb659539f7b55fef33e42794217a344bae925d5d7e34c12002a1ffe271'),
                                          'd343d0bebd12b89e3c975edb25d0accfe769c0c0154ac7f80566423288344ddc')}

PREREQUISITES = {}

PAYLOAD = json.loads(zlib.decompress(base64.b85decode(
    'c-qZ;TbH8R(&c~Iuhru_f|8YfZ{EceGQDwo=^>CQAgHIjVvqjsJtGz%m}b?kz4z(vhZ>bCEY^yc5iuiHEdJLY%iV7OuW<9R{nsgc'
    'Kkxr*m;UkJf2g4vE`~<v4&rFsX{V0aUyse^(H*W=6FIKE&)Oq5aZX+$1^ysDxnX<boAKJQw3U-IQ?+*p?4*BO%Kg1<HjbUuZtf5I'
    'i4(RXd|r9=>CPRTSFYJV+NK|?gZ|#_w7W}ds;IsANMqo)+7i!Hhojh*o2fI@R!iLL4+6S=?V9m%Y3VgD!F84scQ)<7O^p3GY%i9B'
    '_^J-ufg>+g4*vEAm*5?9b7f_Zxu1P=w8y<$$DFKeYf588**Y-BWaVHycQZLTiE+jEvTdGMPTkl!1LOL7-tGKOd+o}`RUIfN`r9!t'
    'u|HVsX&wH+NFlS67q%sL)0XVyvh(EC%1eyMt&i4T+IS)Pb`mFb<r?O<!!!NUIGKjyL^|OadoOM8Tnl4tCXja%<4pEyzxU#7MkjaH'
    'UN0eAM}9tfa)4{5k#9{gm-yffnyJtFQlJa<C4Yu(wa;FvM3C<eIy$<8X0((c=hAcLy=He-GkR7{9~u4lW6|4VJ(rU$A7ZE9q<fVw'
    '$1|HGgYq0$m(Y9SCC!7{Q4X#=ja}BEbcP&iYER$!!?=p0)%K+mw~fjAGMY%ug=w_=i?r2LI{}Y3GnEAQ9-y<GD>sh(S(+-|U~!xn'
    ')5T)l?;5@MZ62NlP8U@yjo18n@ou%_@!Bw_3uW;#!84O-OxUDnSaS8A7vRscjM%GBcCV}LO6{~(Y#)%lpZ;kq75HIn3~ByK;0`W|'
    'I@Dv^8b!;2u~r8oe4fVd!^x2`65?4MF)y`STM4}xYfC2Ct+y{T#u>|IoHWBFFy;?6%s*xvz6{$x-WHd)N$t>|_Mu;6>R3{H{4!IL'
    'r8T<xP*C;^%yF77O<)?&c__O_<F_(-(7yrCscEx+IIkd+4^Q}zE3NI#n5Mo-Hp1h6K=)_IXnw$^n~T2DnfKzZB~6`0&zO(1ak0K#'
    't{0W;0`~l?xw%R6=*+OLTvuuP%^gf2JNS#b2LJIae8_NGcT?DkH4T=g5<8uCjc@_mBbz6GR0r06z@NO)^^h}T4|cWUxzAX?FJk=~'
    '`5D-qUc)sC`5xc^*G^+^qX8Eq_^fz?xut{?_F0f0=CEadNLUi~i0>EVD-Lemp*cmsNe%W~8)xfr2gb%Wb;YVP?pJTK))v=aeCW>a'
    'D8s2Sfp0KsFP#yuM-A62x2_UqcjFED%lQ1#S&MlO;siDxJ90mIH=5#l;nQ}&@5ES)wAn)cfIpZ_4ed!_rS;W3LN%MCCmUG5zP0Lo'
    '$+1R^-I5(0r!`|SPW%}73%!}TQ{gkzjv4}&SARI#dBCN4-CneA+t2WMCE0R3_}N&pk=fqkF|)A<Q@8Po^|rPu^nz;xyUzY49Cun_'
    'X21NmZH`X9mH&O&L$(!}0BaNI;)*rPz{iPj_a@}igq(M7a)6J7?}oj-!!G;*>m2@FM{H=5zA>+UYRkaebx(0JAm5C*R=<0W4Eut;'
    'QA}&BCS|_^yxrpqv9bY-Z?ZUBtQ}adxiVzO_-?!u<KM~qUe|;t;0yli95RM-AJ%UY4pYQf_<B87ag9HmrglD7xGwC);5gotNmlSX'
    'b(LebUL)Ubr{D%jv&MEr>zD1!e=Z7a!7fL%{`|8#pg2;?WH!BK@`}_!kFGgmeuy!P73pnk`qI*zvaJhwBR<Q|c;++N-qklRHT)KM'
    '!#38XB4#O9x}M|-y|(S7DFHJ)@7ykzroFo1uhk@b$njFd4f^*<Ruta~Uw<Vo0sK+S74``E-^RViZhTbx_wh29J;uzQYcq$KvTuJs'
    'm*;}{N&9fgaWs2gTzksD_Xo`yxKC(J%6{IVn3KA7kNFt+CioP{QUOo8z}_|3QOU={zQ^Dzq)+HJei=?r;DY<Ng?{pJFL1PTI_mBv'
    'd&bA4BF~B+smO6)9LcVUbH2@P@oStoI~Ot33s)sPi+_t*0IoRQi@2l1R@nDn->iF`tXChM_Vi_dab!JRT5XoMB{g@D<q`AW!OoiZ'
    '^Lr`FsqAB+57-cNh}bP`sNy$nG6WWG>$=6+a?G4dpD;okM(8u=n*n@Di+v7!<hG<E*a+4XH^cYYs;YNzCY9n7`3?Ge)BXW_&3&fe'
    'Ii~&r-*m$NVy^xD)=$8BIj&#8`Hekdc0&H){(HviBhD8p{MlfvfKv`g#>A~jZcgA1jrbwXrCKImA6PWb6jy-*H^(aHA!WINlemL^'
    '=zz-;ZZmEYflF;&IgTLjicWx&*cI4vS$>;!HYV#w;W<_0&9=!ne4i;hT2m1l=e1Q?)>V6=7#t(UOV<j%g&*F4KT95P0~<Qyf5eX9'
    'ySm|V!&mr&(sTCkx5&3fvD;Cfa=BBi%GScy15XF9UMu(!{9VnrMx1B4gpDu&Cn7xSHNKbToi-nG<8czyT=)lY+V7S4v?<|Ta8-IX'
    'k1;ND#?Gi%pCuQ#r)zKPu3j(XYcvrralKe)?1n*^hwtw00VkUVZohQTP?y|UAU=aL3alDe@S;!mvcBXjc1PQldH$rMvOa_loRKYM'
    'xW_#i?npnSc?<sso7^}6L}4%8)=uyXo%33{Kl_bw1fR1f|L>SnforSw$<HxPGuwe~GE6Y1`)tSM_4I4|FZEb2*7(W)+{vu``z=;s'
    '9k)1kF3&mq#23Z2mGAOre9YD_fBcU>4)4h>ULM}F;)NF;(*H?+{YaLFaJ%`h;E=?B{P!R4=>i#8Knxn0cPk{O<C=@p&H6_HvWnw!'
    'I6c5>RwGE0?m?y%5F3N1$LzJ@dssU%;yp5mxaPvLN0#)sYN5T<)t=GtkU_)3#?Sz=g##E<|HyN~eDbmG#|FDtGr|Y`E9M-35Yrnh'
    '4$h#TF4N44OnTlkvhDr`j3i#B(i-TGC~JVHI%Mm_bM}WNSyH0J?=y*5A+nNvOkT_xjP|aq|4=(dv$LV^vd=^P2O{1FXH4|``6U2a'
    '_qL^9-)7KmN4hTM_^gI)$~=;{nHpi;K$lcxD{7?7`5HufLOQILSoHH)?tS~^`Zpx2>4%84WGy6vJx2jshIK*iusB${6py85=utJK'
    'qip?w1V)};`;+y7!N4PM6cqR3p2c6&6?A^02o3899QG27iOLuv>aF)`4_Rh?bON({v*8sTS{s<qFP{PYVxAv%UB6m#KcVN*n%+30'
    '*pmm}lV0Er_6~bMqjuBH==*3^!m+FaQ_U+ygs};xoa~P@?uhg}Q-7%&s$eWl|7g{91x!13XN(Vc6y*m;kZvu+_lir`4Gd&uV9)s8'
    'iE1H@L+l*36R90P^6J_NYdgc%Qi}Zeyy11#?WPvBQa$P+1GEoIFm^w$^l{cwy8vIbE{a$oS4C+4lO27ReQuwrvWR)s-r<edjwah@'
    'F}KAx@^WlvGv$FjwT@&rqLLw%v!(CqU<yVBk7})-oa7R}cL@Xdza!N#zw_(HPi?D(>-@m$ZX4ckg})`p+26U*Hr0pi20Z*qyN=Fu'
    'FSFgj=;RF7M-R_)X3`o=^v5_cevHlCi6XOO75040=EPBdY>5gdt_?(#mUzu-M<IV8)<w*gvsvXznb3RMCO-k0_mx+$bh2?gGl9Mu'
    'ugG{@s#1iKU<ub<M7Hc$Dy@O+8`z3B%i-in?@oFCkk{IwF|Jz$Yh7t`hrhQoCixom&+qV~E^GsK7U^?M)~;R+&!PzTgX{rOaQzx;'
    '7cJ_CTD1Po{sNeI4fRAr^l|3&eAw(}a)6AUocZ=ba>N)3`J1uj$H3&)?`~zS3)zbb8vG?!Tm{RFc1K(r<DO<o_Z2&M=qta(NB>?2'
    '&==eJp@?!+`I+yw?2|*n&PcFt_LJ~6(KdQTWPTlJ@*{aTU9F~FwX!@Q5xeemfvF)yePCV2+&1O-z`Fl8SVrn52K1l#$wbWU9w+vn'
    '!+l`N7~AX}Y>W%Pa`eg0`JR!l4sZG%oB3Qd#ZDFt`)bp=16w{YqjQtVlX{IqXC6d)w5QB;k8A<o_0C$fxHwVOCceP?SF#2kbjeF4'
    'u8zQG#WXj_qQ*F%Z?A+=56@g8TPV+?xMn7uoW!|;kv(a3##r;O_zK9KY##m(dLQZ$*1mT;(gC);LG}TAZk}HwwZ{ITtjjO-bhBq<'
    '-ZC;=#6Z|`KHif~cGqd0)owl}WCdU4CSLxm%oi0H1S@VmX%_s^kaQNW)ehlpanVitug;0CfuDZP=C(Tca=i8jt0(<xM9c1P>UN0h'
    'kO4y{zz*g&+~0O{<~#ll`r-e_oZ*mPCVR$uhQ<Mycmh_D8TM;0U3E`8M&K!pmu_pXnNIpLTjzfIqHkE&g*>%r%JTe8{hy)d1n~-7'
    'V;XanV5pHSAhYS3DsZn+ufcvYYG;13A1!6hV2@6B8)<X(Vn?b%{(yFi;CsK;(akT!+F((4=Doj+C9e*7nSH9<(YTVg(czzVXJp32'
    '!BUb9;TAq|=g2|rHPTXnr(gT(*Pr_8zd7FrHb4Fg<Nbf&J04=kBmZ&Z4;O8d@dschdu9=nwOK>f=YQG8c97?Ws%ce@;KT1v$WG}0'
    '1M>pdAH^H;-M%Ru!4p!)qDtvxtA!VmH`)GH>zpsnM%}$&PL2$26!qkLKJ+U1&|k&@=DzW1cZGBXJUGDXYt$<Hzo#1~`5U(Ocjq^V'
    '56&Hb%s4g1_IJ*3x`lksT4#Z4g4{+@?JE3)E06w7v1M#JJHNZ*Jd0xY1Kx19X`K1`Z_U|;zOst*O<#G;m}kB#kKMA?aJqfiKIcQo'
    '*N`7tyBO=a3Vm~4RPr6YqaOX=;JzjM7Je=FRe^3AYg<;o;))Vi!V;c$agEQr>Qp^Z5M!E&v(aPd==wKeID91WO`Y-k+p_Dm4~{wA'
    '*|VS;YopZ}_wF)Y_FKMZY_gs2|EB-=X-uZrOTLk0_SR{Nymj7qd6aur^Y)^Sz`wl#msH8M<x7Cvv8mo;fp$y4Q$N=xc&F<bG7Y%e'
    'eXDI0e3*96+*JLRRl}Z_-QKr{oiEY(M8D<Nd0nMf)M3JQwGJ>ScAdC0067=z3iB7cL|JDG%k>DkoZqqv?OV39^<bU(?o|jIrCq!e'
    't(SIxvG#lyv#F8{hgeUiwc-1a*FCD{W;K8naaCttE2?styt28(M{kJnhuN;?Cfhkdp6}9*H{CZYs{i=?@cqH=V3VIi6>8boA{Qdx'
    '+f?IxtZG+9-Z|0Ob`n|_uoa9=QC)@3=EV+PsoNlvV{z|K*N_Cb2Dl1KYq;$sm)62HsJq>qJil&mb#^58L*fH0OS8Xshg^%|&V`XB'
    'eSc5ekE^3YshQ)ScD{h`@a?u6@N9348hHG%BzMV9kf(RlZ;MP%z)a{{(;DVd;BhQ7cCycHs*hwlh!5t_tu@t-ABf#ekLEylF60Z}'
    'c@iBI0mabGy`KJL_sh|(SFpYkHA`pbSf0TBCa>Q?)>OO0-0}UEy3l}=Z@hESy&P@JF5ASToDg;)^46>Z-&EJ)nRlH;tMWZJyXzIT'
    'tGAn;o0WBzFmbo53tMsm*J^$D=DFT^Xa9pc7dG)T;@ckjj;J&0k^bp(whLNR{O@*{H&vOl&Zyf2F+qwjK6QfCU?ajG-pTcCUFmk<'
    '+H8&+#LK+4`>*1e5qu2g{=@&bYtAsmwZdG#59$(meGqu38l}?bxp!J8wFkUm&1BcWRq#uFXS?`+N+06d-<@0DQBa8&#oW5*6a12l'
    'zh8c7!=2u}4Rfq3br6Vsg)8DjUc)N7A=Df@V#kO&g9al7_{sP~ex1a&$Q>nFECr_IM{)G_+{!(C{abW7Kf1@U;@I9mj)=dLTD&l4'
    '?V+)Vds9Pu9@ksn-Uch$*<Js9UW(Y4$z$%7;<WnhZP@y@pjv%mAFA;}p*lWw=dl02?_g!Wgjg@;o&7KT(8D#jrctx0o?hRJ-Th7c'
    'A-XUos}I;{<=I2T$ZS{HlEtpz$FRMJtx!Fda_BJIf!^PC@>MYocaAl3zEH-;qn*_p4=a^zm^(Sdbz*n$=l76}3~%x70Uyc6`VvPs'
    '9aFwywGJ#F@%J(7sv~ajt-K5QhMdWNj9cFMADaQjos{EccHgSP?LODUsSZauBl9KZil4@|4&U<*gR$7<CAo))!@vjDGB6tOkq0f;'
    'b+(qg(*W1PuddQha~taL$&JcAVwYZjcF9NAr(5!m0vp-$6VWB`K|9`wUt10@XK?D&HZQyPWbvdX0z>0l2T4d{5Xbh&pOoj&En&F$'
    '?t;AE{z9+FhoeSyr}>7Vtm~nKp^hT<5X8RA-Htipi#3A3(vdej(yI<W^I4y_XHv&Rw${yb>zh&t|G0DeluMl}c&+^FB9}6~l~*4{'
    'v@iCa7Tp?<rE#zm1?#<hP>f>P6Ned21c$vn59_+b+3(0pgulUfz}ZguB%@BjyKeq|vVAnSt#(zabD~ZqvWGeOF0En{HypJ}K4wjL'
    'yxR5APIMSI1peSNAKjbBv;1BU`2#rS2kwWx#<iS#J&@(I*LkS7l=4yHq~$q%8dqTQ{I!0o+^;I9^Qpkj{1G1MUc%&^oIm3oaw+^k'
    'nIDs$xPwXHDEp2(>WcaNBAx>G;OW(z13utqTydeCsLtXK^sVUB6g+iV;i=i4=Pz>*LnhgC4npHryObXCpi*wCIM(z}KBvMTne)u4'
    'gR&gkdX;N#`PeXy{c3LX>fU$Li+p=`chclGzk)xB*j``-F}Z@RpYhc@Tl_TtO1IZ^yF@(n5r2K&E0|K(KCK1*TP=5{E~s0~Hi=Vk'
    '=XlMrMhEUlMm!=;oOP1s`TMbqbHRx(SLea}sB6|s7FkC*=~l1Vrjv}VijIrZIMnU#iIWQCn``1^4Ch*_cW{*PCpkT^J=l)dEo1qs'
    'c-;S#L;bG&iGx3gKcPRMPSgB3qZ-vB@p*sO=OFw)*EOD>7(Yhy4nNF^%Q?+Yb8_O5T&D@!R39TfUduT{Np2aA?_y84(mPY|AA2)B'
    ';-2#QsJ0%scl{C^i#k5l;<-bylJCXM2=WB>V55TT|BHDu?DUOl5Aeg&qQ9a&$;McXLam|C*UBq6v0d?@U&bkL80b9rXM~4BevOw0'
    '_q{ywuXnlLOa9&O<WyV>c+5c`)Fi*=p%3>ixgJOz`M0{?<2Yw1jya+Z=ny${XD%5FwLev-vo@cwsn+iP3I}~umnDwN`xy_p=On8k'
    '&g6awzw-l}Fc7uLuh#PD88P{~6ENR~t#0|0R;5F~zqT#-GOEdmlW5k`JnSf6K%Tp&eGGrFs+_dJ7(3dNp%Zj@ts60>PW4qfLE{r|'
    'qnvB7II6wo*`a#wtX*^K?VU}h6Vf*OOZct>#)`%1zQw2003vU5;?ilV>s{Q-ed0bl@j?9^SMtH&kF@X09oM%!>LDNgdT+WC>x=z6'
    '<eR$Wno@vxkk^k-h`(tTLqv^CW*HxmGah}itzvJp!f&V+cUMo2xu*wtC7rrEa&5cd4GqLHgShw=a*d$tHT`Z=7it#Eu=ZDn^Biq8'
    'vw%_9rrL+^kvYzuoKT!bS_}f{C_Z~+8;}uQllM;|zDJNHVs~Tp+Eo=D{FQpV%3aZPN+XNq&`Uq%6Ox%8v+uVy{1WsIJ;dN{XNs|r'
    'Q+yV3%EzGnJN&(WP5E>bpVk0Q6X+vaQcM`?w09I0r%`!7d&G4}*gCMT?_eL-aa4_KLdK0!?Q694htson-JZt4fM0Keo1Kqtg1A}d'
    'lPVI`4937E@+&%hhB(u^yw2Bkd>2^PRr)&jKQ#DSJ<a+PBV|T4icJ35$u@mUoYt{auEE`LWAeQPo=O~NEl#dou5ZyL$FNeZ=_&bX'
    'qln|%CfncIP#xul%Sx_|e8P}p>i;CJj@YFHE}aVONr98%dii-ZO{lJ|tr#you2Dp`35=P~t3_g5h2Q8O@cfN9K}!6xIxjxG)1mxI'
    'C*DgrkC<;?-?<wDc@^?BxmWdPz=dH>725><!}b+=y0ZsfYpuZ5`%5bU1}1VqCxVEFwcP}HDeTXasn?-Fzs0oIbi>7&)^!vZGY*`?'
    'q~b(FQOE1F6Y7p%S`OlMoBZd7PWyRj<5R9h@+{XCmqWzwq4qRRo3R@z^^*U@Ge?_o-QO+c^{KjU^&8|G6l=TX&Np8oVtMuXobwp8'
    'PrUc8zxGcvK9Sa>JpN{HW^i)l$#38#J28WJ>t&}Ic~1pndct0hBF;~4CowaO(CKo%mbgEka6XWH!FT8c2<w(kSY}=Gg)Cw_)AOQE'
    '^9FD4oL3W50#A<lv^nE+=o1EZ)Dyid*4cpHqm$FY4nFHdoV|R~$`k!SKg8aKMqT{*sp%{A*U>4JG4(d`T$&V10$VQThjmi^;K295'
    '*6GwJbhR{{9o8y(#KKDaTsg22@>wOhvy3K|v7!D~wX5#cZcllgd*8qCA1lgFfR(JvAJ~Vi)t+)1hpmPd!7u%m&ohqW4dF39i+yG~'
    'J>=0z)gQ}Qvub;_LWbd6OguN=<9Q(4=<j27DjO#UKGquq3hyE3{;yikI=`(ebzGJYpZ)<C;oK~_#mRepP!3433wCj^@!a>!2hGgO'
    '$w|+vx!I@FF+pxGlccZMmLKrm7xYV~>-mIc!h84BV?z8*VAjg~C!J)a6Z7m(8{)Sa#om?-Js-6z^*Z$>k?$Q4hnxAS;^U_p3avMy'
    'd?SFJ*tD++pWD8^hR-MPs-s`B(=qjHrcL%g<61>VQCYS{yvpn1gP5?raZL7k=jCwy55z1TSf%`I@mKv!0RGLj+1Vl<5#P?nD>x}+'
    'y5_oh*gk`6?Z~z=4%>rIiCr2eWWK4})>`NWe%qI6-<3|%w#lEI;Df{)4SLigvS9n1C*W_U6vF<%jmXw@@>j%fLtIOK`%HNoaXc?S'
    '*^03pJ`JveTT*`&)jYVzq2MZbc97K%z}G2<#q$tD;YX+kW%Hl2<wAaUwp@IFSC?x10~i<ud=^9QE3{Yh6Arxi#7SrEIiGK!m~86c'
    'Dt)qTtdIHPp5GFZwyqlFNT-0^#OJqxkRPbVS&mV}dtbmQ6}78f#+_EGbyZ35RYNJCL4m!exOW4NdR4o_a5d7D61P6PGM&cLMV`ud'
    '(oeuPa1+<~O$+d6w69LSV9ve)z61C$z@0ogsh!`~pTZW`zh&><P=}5CCqGoq%T9KdNREl)WOb0{*^~WfESKb-K3`tDt(rdXNm{pc'
    'rZYT_xe&VVx95{tNq(7JxfXJVLwtABaS0D4|NeZ_uQEZdC%J>{+?0s($W^4=2kq?oFZimMAGkSkj$xb6;4H*B6FOlZL8oosno>S1'
    '`VBI_Zj+8G&u%7&u@|j#ZoJMPzRBkH2AZyV)*|9a#u00|7H^#?ax(FKe#$TJd$3t<l&8{LK#YCfe~|YH{+3PGi32Mew{9Q3!RjRP'
    'RDDNzP&O{%U}LAvGVV{>e0A2li;F&Qoi))vlAmm!ENZ<x&k`K4!1%hDqxTPR%{l404o(XW_0#wrmwi?{J2OQ%rksR*0NLNMu$3P2'
    '|BVsQNq**RX8+&B-RVpaaeKG)+ze|Eau7PpMfT_I)t+&rb6xZX9}%xvPGhROxgCjo2Ib8gpL*YB|0({jYsE7xt?<ct-<VsK<=?f('
    'KApRBW$EX<DrPw_rv~myXY-63pJx7jUU{O1M400J2I@EC++4)p+Hd-EQ8UT*x$K1eD9<Hzc^*xwGfU84n&*S?Z)<0k*T1W|A;v-M'
    'zMMSP|KtdLQ;q^Z9Y^5qJIFPqxsvTMho^cv*D&G;F@oyC3e~6bo<4B<BlB_S>pzHxLPr%JJ;>&6Rq_~~*OKy_TV3Su$LpBh>Y-ej'
    'yH<TS)kssDV(y0C$OHM!e;Uv4a-gzaM<>QPtu-l~^Pv;#@LBF%e<gfu#}?<0*4bQom~Q|b(%ZSHrW6$RTe`2Y?aWJDp7z>nPM#Zz'
    'H<H9$n}e^&`gCfg+EuW$M&gZDRC{Cm_f}fey6BXzinnWVO)BHgMPF7nwnT3sLH;Pw+hT0m+u@qTLA(vd;x`E)U%n`aF<t1F-rRKH'
    'H*`=Q0KSlOLY4M>&BCu;MctO`t<*m&-ZnJ=?h@V)AX%hKtMwntBMi*T-RLZvEFM+)<nRH8Zngb?fK$@`8`qX$vj%MZ691l0qqk=e'
    '2HG)r!k&Mt>xi>);B()O$Sv+Tq{t7l+OwVB^dR1(ciD;hD)dHtM7#lrZPcr0SSfrd|JJ6nnQHG6*m!ns&$Fa?w9VCOfoD@b2yCz)'
    'sOCuAo55IhsHWBtob6_(wD%jYeXf}jE)2qDRH}pj<CvJ!TVTu)y@3TWy?J&y$IxSEme-21-@(nY-vwXm{z=Yp+voqC8h+lpUg^2b'
    '`Ocjj$~`0{E@qs?I|GCdhaKMe@SMYdi_6l1YoM|QEUBk?V$`jQoRp7=%x`c)&f4FPlik^&-aPX{y_^I1xPbBxdMlFf`wHzP+@Cq;'
    '+|eN$?5N^>27FGp27Bl~y?^SlLac+2$ofXU-C??G^Epzo*E79|1zeiW^^X+blFuc$v>#R15%1~zRqKl!l=C0*;Q}wF^Z+ls7x(lh'
    'Wg=<<**I8pK0f=7pUi{aXvuHapuH29&$x<wm}=Ru0oW{bvss_?PUAf0K16LbiPtOoEI3x_ETWnFf`IuL_rMI<hQL$($j;s#RP|#S'
    'x0si?^5^gP?13q5;1^T-THy;4y{`bi^h;T0G4*s?V>2Ghi_5rH%K4<`$%(7^|7bqyTD9z51yZx}u7dHVeJo*7x2@Kvx7XR_yqNe{'
    'HHQkh-YfPpoAj2Hcd8jyZLBJ{Qf+|GB6Zp!;%;|2=*RBhxuL_Ce!;13wkB#HhX=Kf0quRhu756*ale`EmFXXIS&yh!hTb0Kc9b*i'
    '$!2*<Ha^8^@m$8rPv!?~Ql2VPT|2i8_8G`IIESPfvpk~x;$VE89JS7K__o%&YH#F>4ZW>)@tyFErL$!*afkYnb6%?10SDkRlv`HL'
    'c14vOfn+Xu$)a?2puFc_?Q{L<S*A!?&^s&CJl{*=C$6D$4di|gx%GSXs+9UUrtv%Ez8tpxmA!|hS@l<<2c6E9EX_$%n`?EwYd7?{'
    'Dr>pV$YK?^pW~&U_K}$1yHt;aA7MY&{k_;Xmc{-&>}Bh9o1&L*UVSgfi1v)ShvJ;hZC^sYt9A0ZC#rQy^m~?nBW6>tj*)&fH|n<|'
    '-sRJqXLCCc^P@Ka0l&lz=}lnL)t)`q#!-v*{=1X3-7#m<d@^g%cfyx~U*!Ab?}@R#?Z;p|<UDj{&FS*{K}0;}y^}R@S*kk_KN;oc'
    '!(g|vi1)@0{Dk_KS9xzB<xw`(Q%kuMakjiChyBEZJ|*N;kNSp=^qv>2X_CG5DDNRFzrC08YVub#;!jIH<Hx-$q6YhU&*sL#^S9kX'
    '7W@|AjDwaqws=b;^SEq1ut7eL7Ck=i_Q(JJKU187g#'
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
        print('Separate city sections already present. No files changed.')
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
    backup = backup_parent / ('EK_code_backup_city_section_views_' + datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
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
    print('This separates Attraction, Event / Festival and About Kabankalan into individual views.')
    print('This changes the City Information view and template only; no database, media, migrations, routes or JS files are changed.')
    print('Stop the Django server first. A backup of replaced files will be created in your user folder.')
    answer = input('Type APPLY CITY VIEWS to continue, or press Enter to cancel: ').strip()
    if answer != 'APPLY CITY VIEWS':
        print('Cancelled. No files changed.')
        return
    try:
        apply(Path.cwd(), Path.home())
    except Exception as exc:
        print('STOPPED:', exc)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
