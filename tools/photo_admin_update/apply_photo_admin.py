#!/usr/bin/env python3
"""Install reviewed photo-admin changes on a schema-compatible local project.

This code update does not run migrations or change database rows or schema.
Future admin photo replacements clear old license information as requested.
"""
import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import sys
import tempfile
from datetime import datetime
import zlib

FILES = {'apps/info/models.py': (('68d60dd3783d313a2c98aa5671021f1d0d4536a8613352290ba13858f156bee2',),
                         'ce9fbac8c78c5b916b1123d69ab810f0b61ddc09e121f6538ab76176aaaa3533'),
 'apps/info/admin.py': (('f3656fe57d9dc57f87a325a374b5217b56f3a6ca0daa69d8ed7e85a8ac942d53',),
                        'd209784cde66445bc8d3fe1123de13bdd602335cf7fa35cdaa89635dd3743d4d'),
 'apps/places/admin.py': (('40ea7d6f2dec8b0e044f87abda4dd62de9e0fa9afce23f6b236a20c2551cee5d',),
                          '916f98d9ae61fd090ff9f4571e53b1ebf5902b7e1166bdaf116fdcfc03efef1f'),
 'apps/places/forms.py': (('ccb2fb391066a9b909cf509bf0bd31368d74584221ecac612a94306df63e3b7b',),
                          'eaa823f14c0ba07ecdf86f51955eb278469d3a6f268f2a37139c85000e546c1f'),
 'apps/info/migrations/0005_cityinformation_photo_rights_compat.py': ((None,),
                                                                      '67d199373f15117466b1008d602d99a75a3f31ac4cf61a14f36e57c35eb0206d')}

PREREQUISITES = {}

PAYLOAD = json.loads(zlib.decompress(base64.b85decode(
    'c-q~4S##prlJ0-mucxDr1g5Ig5$6Fg0x{W4Lg=LfBm=S}U>9J98~4B8%v^((ChXcn5BH&>s%((fnB$jU{-58Lhr{uo!EU|(XT0~{'
    'qT|0GZomD<Z|<)9v6?i(Wo(|^%8#?#wl>STepyw!n$^}n+_ru6E{E8Qjg!?L|Gt>lcB@<MeO0N&Ry#U*ZR6%Q8+X?kYfJc@ciH!v'
    '@$k5ChIgwqJoufcyNcZpFV?qyJNj4!+taEtj#iz)c{(>jcYZm%Z1x+gS>G%w*R59_Y$o$sywb-tuRYtZ=rh-QKN?4Go$>RsZ5$RA'
    '``(-Gd-xspr_r#@@nkd`&L%VC#d_8@R%~j1r@LKL$A?wrDd;!r!3f6a#pXL3hoyeMJ=KgB`=0x;s*LFK<JkCcoAuag!879M?A}t}'
    'nc6MWrSI&9+QJFxJG1I|`{oQb-JsD}RE8g`Ij*4zYh#?f^!H6Wv|sFI-LRV7$dB!_-?WbKZ<GDI{$aJ;$b<3wv3a!k8qpt`Yi&Af'
    '8590}oY&c_Ha@%^8@mm2U+so$A6ve@oR1@T277-S_a)rCP8xDAV6HcJ9_?1)DSDf1lyTOBMJ0mq+xLD*-wXP6Wh`yu?BFxnw&qTC'
    '`Mi;4PT@~$Jh`ZIhId@y9N3{#scl#DnPJ6rM%GK*^J@3BaQJ@lcl1W=Z`d<!)t;rsJgRKBUg#d+nPIQ3Z{JMg=)xKF+Z$u>KGVf_'
    '>DjuWy*Z5t_e-9saJXMM-8Rha=r+|kH((swHO%SkR>%9-sdY)udAMIyqIcIB7|K~aFDl!Q<$M@<x73{BUGCPOU$xg6oT1p5;W+xC'
    'IkU}fW2BF}Q|;;44CH!m+;$h&BXpgO0sE-Cat%Yif8)rj3~x)PLFXzpCw5Q7oDS@{@VSnCTEw;Oa(-R=PWPDpjy;*S#5#75aL0eX'
    '+T)u)pNa2Z;NEGlhVNc%hf8Nvz7MH&O7F>VTF<Ow>RqWdSfbo94b647+H3kevOnPv&Jx^>X5$EJ6<KYNF#*gI&WPXM>Z^J8yqHJF'
    'eiPO@_Rdz*%0DCUM>MbdelywG+f~qL;rRr)b@QG5rhjWV%lYZBn!}vut<9)noK|#?>-&*5*o>m^G}Bs}Ve{$Io4`BNJK7AzeE1sH'
    '-z^j6!E6I_I^ext#U7r`yWcjCD=8xy+f}C<E#~8z)fsAVCnBpe-n-5a{_Y;!%2tEV#I(Pi0et@n=Nrj)w8wD2%mCzX)DIeccWz(k'
    '`*YlH^WwqXv)XpW#qU+N(TcAbyzhk1TD9R^!<gJj17$qO72}9w^5PlnNfd%UIQRKHz4rFQZyW36J0OdM&bZY;R-3nR9D!^YfgCrV'
    'oXRy?#lE(D)~<u+`q6rP){c0WK!!z5)xNEosb|}>@XF8lHgi{7moGf~zJh0h9{J=hWMm4Q-$C=TS;W`vDn9bNDeh!+cd88?es}O-'
    'UETC}o2v>w$2^PmNZ)rmUO4vAf7aUz7=xRZnc*Tb;H<#Ce%5E+&W_S|2==hkSc6P`@}ITTbJ?Hn>ngs&SyIQ=fOQ?;P^Me3N3hqG'
    'r87Lh?<17wbY3Qni$Cwe9>6&V`TsVl2L;d0==R2CG56uzrS94xE6d?bgKV=>GGx{^?n?)Co!y18MQ+8GXD3-7?INDBfO`SDB63Y*'
    '>!;Vcg+I5!HgRWSA5ERkX>3%TiW$0m9pPC*A98y|kNkG)TUHk1ePX(&9>Cqbtia}RZQ~urTXQNT({FITnJiXiKnL`9-2L$2oULN>'
    '1mC%=I&kjh7kU<3*G6UyQ#Jzp9ArJ&9xzAqNV@oKLUzIdzvom*_mIx#>l!$6Ua&qvW9?Ljnim=CUI*?|dm-&DHb$^LU`()gv9&wh'
    'VZGu$>E!TCV|KJnf6`dJRq4B6Bib6D^BVN_1?B|$0PKvmS?e_;!<jU`!+ei!P}5+2j`01U33i9D?PgW`K8x);*o|keqS$vK+rPxF'
    'vjQs`)<8~1V4vDv#SB1qk=-(@47a!+J#%Q!ZsEp*yA0>1hI2t12xSJ!=)pwOL59A=o#OhTejPL$S0Bzjt@UnjfVc2--Oyp&x3qnL'
    '`(lI4t@T|eOx-Q`tOm~jnFIRIwr3O5uxFY*aWwsP+_DE>v60~OGe@i0AhJ@rZ?&_JtHQfpt}kJnM}8kb@9EL&q<i<B;o6gH4R<}r'
    '*b$x9H7)z#yrHe<xY4Yl!x~?6cQLJ(yIqtOpu>LR-wUt{CX+@LWGl#J)XOK-T_0A*MtuT$Cc49Zh&=_L!p6Ng`|WEDWQLH@*FliF'
    '&!bfp&SN{Oxc2Y_dwB$#OLIZaB(`5l1_m$&uq8nsG?{MmsuAqBeS&eonYO`h8{Wb0JFMU=EkLJx?Q8Vbd<ukY@uq_^*))ZFeq6O8'
    '7_+@|rR}%{{d&E?T?E@}WLRN{I{Cw&`+Gk(27e3s6lB-1maL8X?$KZIZjcQ}{2OFr1NO*=v0Op#*CKa5B6|V$LH9c3FKkwo#byEf'
    '<IcgZjiYyzPhcn9yb9@p4>)&lf0zvP+dnow*&?v-;OB^Wsrxsa{I&ZB{txIXLr1&EpV!{`-4(Xa0e*gebA}q)I6j<JIBQjSF4zEU'
    't-v>e-;K^zAkTf}uQ>NG#@({R))Va`zhd5Ty;irz$%nPX_rv*uyGLtuUR1-PF{|UM{`ql<y^dh5eK-d*aSl$f4;t73(W=@wy2?ET'
    'y9DLG2IB@9ILohTY~Mgn!Cj5smzDHgeQEw(cNKK!4(?|a{T4clCzK(4jOv=z{`8u)T^Q3y%#&gp=r6C}ZopY5JDuMdF1ytG+PeJt'
    '_v5`Bqg{sc6Z^5X+Sd=*w-1+Wbka3od)hJi1TB(XIy`TKI@xOb9~ggu{fG76JUC;+clv%x&y6FnD{#M3HnrQ1b|8E1uhZEPZ3+IF'
    'HOR{?#$doNrk}g9sl)mi1Mq_e(nm%A4Da1|y~y~BWAJrcdyIaSc;D7{#ve|l_TlTs)@_fZZOzZwJJ=U@n9tC4#@m$r(jEsO`?h4e'
    'QvAk#g7Kl=UV~i#Ho0mOSmJpw?*)_n9ni_Pafg3{+}M)+la4Lb!9wUx!3I3LXe(pf#|F7q8GhiMUsTK^oY5nXTWosIb+DJ}=-()|'
    '1^;tvyu#czu%^)pWM}WWbsXF-djHuwzD&Yza&Ow;Cz5^M)wx}bdwJn^3;tg}S<fwXjPF*9`E<#%t>dtHsq~*WNAOz?FF}LPQTTOH'
    ';PWw~90!>VcaEQ3uwzs9NM#&?4XLkCt~c2l^><)9G_}oO5^j26YjK<JI=Io;4p#HH;r8a)o6cxWdXxH3<@?p5@4rmg_fs}F+@)1y'
    '+<lNmU^nmCSjDp~_O54qM?*YYWAEDN_zv;xVZh#%{{E)u`&W66nH|o5p4^>Y8}5$D#?%9Sjxjs7M(~cHe(S%_(s3_mtb6g37z^8r'
    'krFF4!Jnb{f_)b8!dYxmOtqKD*CE}ZX80|0FD7*UVn2zGCf}K%oEgd3RG9K_W}!V8+iqhTjmRfKI}+A=yW(-gnezYC_gdz}ZbgkL'
    'i$7k#o`SKON3bzBR@B&fyYT_#KgiPwtR1Y6iSbQ!O}ewFYffACd^D@g*xik8+4oPJ?oIvv|8iSh>P@hFZ*Ml!0p&5tY;42Qha%q4'
    'X~6S`(O1{N+Of}*j&7UpF8Gk?J6>Dkd4Y2pz0Q*u&d44<k7i>tH8=3HFkXeSoqWWphUW(4ihgqEwUEie+S=pi7vyes{x^1By+0I3'
    '9K6?4W0!H)yPmrT;LD0w?Xe{0lK+l!F0-+V{{e9axDS+9h*t5K#S9{Yucv><7=I#DOdb4$+O%yvk|F=w?-I=2Uwe*C_M&>8Y_u^&'
    'EKmBpD4T}3f4`G|lbZKoI@N08?j>>iImoi=NW2eo6z@yQVGP06u4!fVU*7grZKeM~b`q^!1aijMWpY%x_)~wL8ZXA0{`K3xDapm9'
    '9|t>@TWrSeZB^0WEFZRTHb3Ala=S*&F`D6O9-Y7TSsiS-;TG)Odvn8clFgb}ujF$gms6O3<S~#3`c|C18C#dZs^Y<!gEih9>O4+<'
    'hIIqm7;J0D+EW~FmW~7VMhCGM&lo41r1D#}hTGN;t6;ljfAc%pVrwDo&-NAb1Zaof(dK?5`zxKB<9V@kPOjOd*kls#VV_Oq!Lq-@'
    'SW(9Yc@y37Y-fKjVvE`Lz&h}Jo~h;HOJe+SbcD~4jOis~Lw%pb5qV70(+w7Pc7}WK*%LpjVsAZ=<xYj&CGSRSk<1^)2=eU?^7-I('
    'lAJHaOKpScsfqMk)8`tV^Od-&)B*D$&(*N+%5?*K5N(x36@58+mcH7_xci!Hzd8D2G%qzqyMz0>1{wdp>e!+1L;7Slq6{Bu@b8aB'
    'yf>z?afbW;E#p^ALH9=JFQPxfeCHvav%7`9KlmxIHX-Op+AG`_&~q4n<#Ow?amhCw-(PNx5PZ<{syc!--+uTPb-xGX2d^fLgUB1v'
    'nV(!>O=|F5j1|?;XAQ|_W4X9!=~(bAvqG__*gX1_cL3Q7pT&E*YBnM`<C=GSQe{u{2Kvz_zZmr_o~6+qe7XzXx!$CfU9;?39pD`|'
    '*q?*gH@4o&`RSZk9<5oUm?_U8@}JQhc|4ry&VFQ^P_B|}iic>^NAf&YHFfN8*R2gZbNHP49_+9Es*18(u05TtTn^1Pz)!dY86TAA'
    'u@}lSlN=yhd&;N7?+p#(P8R6CMdhmFzNhp+Q}wI(+RaDjh10m8?bc(@Ib>qXn(uTm7N}#aw5L2fbB^x|(0fjW$MTtvb)>jF%F^oS'
    '2zwGNgG+L5z~%#aA7$nX{;YAP`0NDl0JB|DR%0A%F+YJF%i~3uzlfs`-y!)Ax?u)7tRZuU6oZ4g;rcE>uDFxb89Tt3L6;-;WyaRA'
    '+0Ez51Ge5MztNsV3=HZ&)EkR}eG+#G<=q=UAN`o^56)YhLE0zohw^&}_7d5G6gNa$6YlF;Ja0Y9?&IHc&UijE7H0}$mQp^HoFyJx'
    'g7G5m#sZtW`#ao2x>tRQp``t3A9RoxY!2X4gM6~reExf$6S(`$%Z5LLt$S1M)1k@7FygjDUt)T|W^;z1lcEd#|6L1aLN<%|Vj_b#'
    '#rZcSHyVWM*_L|Ap<I~#j<U4yjCYvbjka<Ir}U1oPVyU+&-8a7)6mwNY_s|=onuyG5wWy|))<e6wao3KvX=QX8g#!?{BSomn4J`E'
    '(l!e0IoPk>?znrKcqDt+=fOsuV%!GS3FdA!{R8+`yY-}@j{BUkADDelxPyxU_xKL_0OU9L0=oS?((LIhg_)`U(jMFMntV6UT`PK+'
    '*<V&Glcxor+DANvGmv^6eL~C;73=dtoy`1rSbx8n*2!|MChBKuAV1M(o9(mq*6YmO;(DfZm6Q#9z3|S0ua@$SWqgT`DgQgn>#}p#'
    '(H@@px0_$<-k3}j=M;R;tA&0e$j5Fa0=erOsWpPJ_k(mSf!lr<6Fa`n6Pvvs4egOOG-rC+7e^h^3>(502LHlGyAjUxc9QpXyIb-<'
    'Z()*C&c_~vPyd(M*-Nn5GPdufD2`(7?0bQoEaDx1h5ej73+>xfJVM&Hcg!JxZe6Ros3*pp*u!X}rejeL{2av}IuykiM(jI#@m+@R'
    'yz)Je@dmu7no}9W+(558A;ol4YZym4|AWc6%v#g=MR^0hD7$aJw!Uz`77q9$rXg)99E-JsGo~ACU0{u*4+76}+h~_W*>%mn2jthk'
    'q+fi9mfqV@^^Cz{H{UvqBSw=)^I8p&SeQ+ifwhh|ZP=QfDU#kgfyZv1mzZS$EzECk3vW7jbK>?6!6LyMcI$8Um<f1VvfuA4lSc_j'
    '>a>nYv<kHAJle4c9Y>wTXq`uxZAL5j1`+^v9jr?SGZJLgqo;kqnY+!WUKTlw77I$$1zJlE%PjMga7=mb1)e_4{p_{P9h(zcND^5*'
    'Vp&X6152mqoi}$<Lr)=MULSfq$#>yoo?tERIL9$aeAwkM|Ne0xEPPl8IriBohk6F9LBCMsa{^KdQ7;uj%E|B8Z5z=9coHV^_xb05'
    '<#koZd4U_eXPSjPw<tHpoeleRz4zm-wgPW0iHLA1ZW?>PtsjN81kYP9JLA*JG=5)IFuEe&byLOzd+8oi5f*buRt$JI(G)c00?(z0'
    'w6yWIZPduko$W2`ADkyROW<LeXZkn16UK7)oUSG#HEr|abp~gNCN5ZWI^QE1*`c|pzn@gh03(5m`E|RB*x6=Mr`E>Lighb`_OuFG'
    '4n2MiEMcd6hw<@9_yz7AWi%NY^a9SMW;RE&T7NXVHl~sBJh8{FqeX-eAK)D`{ll^noe+Tv9?Ef5F@AzYE75c-@Qx_!>sTjmXP?2V'
    '{z*v8whiyu$Or;hjXHXngzSJjHJzCYM{ihDef;WZS1`0r_RJ)yqz&qa*O{iTXWG>sllR(<$P;y7j$l!ELHBJ{9iIA=?HRS)y5n!('
    'oGV9Mqnrp&J@Xp&Zehr!JY_+hN>|7ILR1VxW!vjz#jf?>KKbbFsfetQd+hD#8)gy-W!gl`ulDYDY$1<GmVo6Co_hC=UKJuY&{F{^'
    'S%JN;;<~`y!0b>J<ja|537)`9;L%5kN(0ZKX`Pp`fm$5zdW^_u%q;afRxq!$PH*q^(~GVB#E6m@GxPkdpf{<}7{T%*G<1IlRyytV'
    'Y;Oe%(x4W474Ua&5~9`FBP-A}F7O_*2r%=DNKsf94d>GX?+xxKT7P%4PU2C5sDl}dNh6O=aLz#k<5*DBjkkEG5J}^A{D{!E9sk2>'
    '9!|{j9+9_%QI{-22~i2lIeLufS-@WJ24@AehSu74wF~zwvNEG=E{hVeHJ3k!cc!x{d>%2K4-F$NC_k1kN3c}kOxG~`4_^N4NSYGl'
    'y9+-@>%*sr3*K|IylUXxUSS=4_H(W+dzmPej3TsZ@Y$KLa8Pz_;l232^<qNj8nkQ#a~kYjcrL6Z{2krEvpN$>nvLnuo2W8p8?V}E'
    '0d0%MFC#$seW!w`g)3%F0=&-!&k+0imG>#1h4rbhb?i+N&vDfmZ^0YiqDPA|3C<Hn+F9m-jR!N&xUMjN(94uHVLzia5mgN2H4YEt'
    '0nM-4!ZwbWG3ejwx89`wJ7%3RlMVX>XOyig{+!9@Eqgv@z(L-im6jSy^T%dDzuTjHOYhfn>o&ZPZiDCg#cJ-s9-uLhr8k&7U4)z`'
    'v~+WG>AxfTdUMF!rx4`hkw+lcLJl~UEu81^z1L}wCo7O8X_;e&F5ZpG(+MNIU}NYDs)_+`zHNYK6k(R^v?6`A*}$3Ey4AsVMAhKk'
    '!D<bP*hob4P{=8~+ZslM_+2vJKp*&Y54(tTIlRR-kE}_g^gGJ4<s9uP{Fy+~gHCH3I_h#n^!J0t6!av>W%DM!FS1qWsV&i_Vt1K;'
    'H^Oz+2Vi4?uF(9-j}6FFSuF$mzF$=vh@RY&T!=l4j0OHYI=bWyF@*j!G-muga6Z9ftl;>&U{m7X==H)`t#(6ZXVIMSjA5m~0LSZN'
    '7Nr7KK1M1kI%f3`m?Z=GjTx`4$D*R#n|ez2NXWligQLyK3-2%HU66Yx&=)2~y7a{ky<kGKoIxLkB-5B}Nzs|%?Skn2pSWfW<>wz<'
    'jN0&XAu12l3JUPB$)o6TTelw@!4hOB%;hXRr(RoB8I6oG-443q1IM2BuDb^w$!BP0<}oQUko{kgH3B6eWe)06j5fhIS1=A(53sxF'
    '++E6bZ|ZX#Ne%ajN2rxE$fI*|J$zs8Kk8ei>*zCRUlRfyZ60TklFiH;#0;MiFvOdE_jHCNb}CpAw&mWg980EJiZY_)4b62e8(}@d'
    '9oe&YfVcOqZHCW9QB$=04LAqj$21!sgsO}T9+}68HjHCl9?hoccoi#UEbt|c6s6+xr~gx=6nuale+REXJ6O+`!ttb{c9k0XQ@T5P'
    '@NT|_u+OQnKaQB9tuRDH7oupUY_5upH6MxRVg*f&BXQ4so}0xE@7E9vR;wh6YaelJvkF66!yOv(y}I?79zOCY@6pPvOMgd^mXBVO'
    '?b)FD^z_L(VI_bDXY-w(rE(jJqgUiUr=r8T=i(Vso=x)O1?3jmd8&Q&{InTNXP1X-{>42l+Ml#cpM6K4$m=vP%1Cmbp)a=>iN6k~'
    'aIYTh3;6lp@)b3y2;vzdU0}PFJcCC+oI#Sk=^O(d+4&~#(vI20lm&=Eh9m0XeZLX^UQfaY8Gvhqx?bGx9-Z&{<19cM5nJZZl<mjw'
    'A^Il{R;gB5wUJYib0Fk{cu&d>XBAtRt)Q$z61BteVK%AuzN)%--wtp`c5XW2u6esKzs^b33uX#2j!=Pfx#k(9GiH6#2*fSO%m(<!'
    '7^StNvD3YQJbCcky3~o%jw%`}%fgUsLf<Fx$q4;`QQ5Uy0l)dSrHrOncZ_LJ7FCtEEMo(@w9c|Gai&T%@rlreI(YE1G(sf0dsQ0|'
    'Vsxg#rrld%<{2_0BHq<li_8+PS&!zJUT-nheoWPe;6rSJam9vn9i0h{it7>Z%DkJ5U`DI#d}L-zR(@hd4`!CmaQ|V9^?fGW0&-!f'
    'r|w6y%Y1yWm;8>3u$AvcSwm++vHew_3iU7lePZw9+Ht?;)4AJ;KZkc5kq8vuQZo@upI|1J&J4~!U@;RG+w*Q;**iQl-5SPe;GVxP'
    '=dud@kl3OOl`6)Ws?<_rB3cCV#r=|zbVNkIgRK%y<~6FoP3|R&z2Mo*#8t#y(!98ZF^!9`RZ`K{m?{?{ju4@LvkFkMwZNYjXAysI'
    '++2)|<G;oEs8Ss5;5uILg~+XtFBjpHQ1q6K3uQt8GAk0c8OSkMFO%k$u@kc~*&W6xFftByK8*`2(%|<Tt<c~VsHk`4d8W9DQcW9V'
    'qT*=3Z#lZ<o2bA6`EUfg1}hgB5~|q%A7KFJ=SLd#k*^*;2pJ`__$`@*NvirX)#k60ZbzA0Zmn4sEw>jO;mxwT*?S6ij>SIMJ^z{4'
    'FUeW8!j{PTM?U&J9jvD6qAwFumZXCjW%7ww#+T&Nk4$Ce`1V$i`IgndBtO~N>+kUFC31o5h>c5?y6VqZHSr(Q8@$4~nXVX+asYo{'
    'V0%g3((Jx~Oye??vg?R=z&L$S7=y{gjq@4B`tB8xtne%^9vIf{WLOwyq6#w~t6B(c$=6od4{OuC<evrdxduMEff<{(rd|c#MO!}a'
    'Z^P%t<?Z<ddVg~Qy-(-!<-K(ubQ(`D74FA1^?2!wzA+tbeP8f9-*+fZq<i=Mlh@gNx89$21=&y3ula1FWGFFEFQDIK;eGV-a&87b'
    'td2I{BRQ9iEejp?2Iq`oTF>=f4t<2^HSo2UmGPD%&puE`IOxaCXB@qDrRrfH_aZ^ay@T$#3lv#07bfpVl<)A*gqCT!hgF9%sZwrJ'
    '{Jw1uP>+m-f1HZ9V1*W(6|kw@cp+o9FkjTCyc)_xluZ@%BUZs_gk+vaCsu)kKf?+^fjH;v0VyQE8tdgTTSTP_oz)p*3`fK`F%Gfi'
    'zQbDjs?9Fx#W&m7;<(&O4Ku)6!g4~W4H=s+MkBF3M09p4Bb<>rV3-B)`#bsSH`)ihZ&EKa9UJXd7%ysWh0HsEZE_@ZA>R|+GpcHU'
    '&s**ETzd(Mmux_e%DubJNXkwX9i#j{YYW5zIlyDTdv3R@b9iJEtB3{A6<5msf@}#EaL3{Nt>Nr|{dPU3*%cC*#j9K@peJ;9vH>4k'
    '!~GKbgy_h>=KTUSF(G}0`WNKIrUbo~Aa2mkk;sx=H*#5p=1s(q6!b335zYAd5Z~d|>OA8u*Po%<;B2PywzbqVkZEU?Fw>AsVe(+h'
    'K4&xCDdY|K$gdvdE^E6<8~lacu)B({SlM|<?58W;4Ok=4(+Bh&woIRF0=aHC%4GKhl2hiIXQT4~{K3V9$Nc7$+dv;KWQe(jMt@I_'
    'o8(#SPD{kZoZ^fi1MMxZK8(b@?n`zjhV(;Z8loC}nJZ-#4m?-<A!B`29wVsm_^oYFoR8-~g>2xcFht40x+01}=4eSqaJeVrUi|s9'
    'k7PWk3$-)lOGSm!7Z4#7izaj-t9F6s2QG|@$!$c)`yZeq8TyW)W!@#b5q$>zdyvssMTV$3u>UjY1+e3W!Y8Hgz+CU>GkX+UVb4io'
    '>AV`D3`HX5g6lZ1{S-Q=d>#)`D5!_fKIV7;shhSuHeav~4U6RUOvp+d{o6Lb-;a?i>2*<Kv3IbmcFY&Z`l|RdGjxd+V!*}|!?WQm'
    '5nERVDMBckig9~Oqhq9ucX&LsY<&f?5Gzhub<~LaGn_RmvmQxK3S<xLC*EI*(UQGj>C#7odq}xbJB?CF`v$Q0;8&`?Pv(qaTm`GQ'
    '5k<{@=eRo<D@RjhQB2&PLtCRNnaQ#!7eqTT<RY&I$yQ5=Jp?^ku#cM{mCp}yxRxw43h3@*K2{YAo67o@tqAZCrOfoTQguN7&~8=j'
    '^8b?_CL~}{6+v%uDR^h*tbzQrB4W8v?nEQZ%qK+jIN>-DvxBj&reZ@7(}GEPbnrL$J>po24Dx9`3DY)hv)gdnW5lG~t>$8*#u%n^'
    '^J2BAGC<yox4exW$omF!DewpQydT^rtdvM%Cj9?OjD)RyD*r@rF4#ZVW0E2HcxYJgvu+vz8sNTnhYaTf_GdoFg?T&lSw6tt4q@%*'
    'v`65-fWE5cKhH2Eggl>L4_pTde?6(dmwx6`T9$OQLqBuQm3Y@Pk9YAnR6Vv#;g^5ue3!(@yXm+hlU+rzMj;m{-l_O)`1vf$ThK2%'
    '2Qt<&M1SX9K0E*UL&48-ckBg`>+JsExz~|_B(0a81lt&5)-FrLMPS|(d;=BZ^}_O$?@R9cBRUc*OBlu@*+c8o{D540jQ2$gV)LkB'
    'yn*}JPl!4tn?m?JN-Ps>M|<lbLkY^gw!ztOL`A|FQSt|@@GE4cE8gE1!iEKC6Lm4hb6=31Go#pXDp$;yKbVci*CDf(7{~ogo;+iI'
    'g#4)%VT`CUnDT;OJEsqH&zJAClVF3AswDV-g~p}$qf~ticNjj0`vr3~5Nj3E`jcF}f^Ik8-zEvV{|hpe)&T9{9D4jKGL+q?Grx;f'
    'ciu&8C6|Nt3E2s=`ylT!`IEMI4%p>a@bSSmLNscc9nQ$;C%8wf;!Mi>7OSL$XWYLy?oVyIPsb24Ux#AVh%tq;YqjLLM_cfF!Mufi'
    'L-L>`Hx{g_;723Ey1<4(q&2gD`~(r4M@ds<9z)`1k-^IT7wUZ$Ye8FqWESc(u&F()ga|H&GCfdMIf!`)FNU?Yzg{_5B9j9t%h6`5'
    'V6}A(83}ppnVyL`k1g8P3&CWm^ZZ(MP*{<O@l5Yl$cplAwYrF_L*3fqcwD@vU`rif9wWGuhK~C51(|F*jR<r+yRVg}6O0vPIjf+t'
    'TE1yF^$&&{K_A_gJ|nM?*1^91Aivto%N-AGj&i;D;Z?Mg@R9nrA{#@ks$u8WA*Pktnfau(HPey20wgx>E3Crj=ZyU>EPJkCW8?nk'
    'P+*+aEEk&S-_L9xXH>}A_wK_TLwlunQ>v=KuLZeFIAg4QSK~^l_rg8Lbt#CA<zq@L-^bTryY={Y9q^f)#79r*<6hbGczg|HAnN>L'
    'oOU**Bx7GStilAld9<;n7&FB4Qy5R$E|ICsRL@?mh4EgvN4-?F&is0WdED6<dw?U#$Cm{QWcWHeHAbQNGSSSzXjWT~v}iWBjqVs@'
    'b?Ara#u{U)-fny++vQmc7+yEcmYIrO!RKM0@4~ldRjUQMcQ^h(7Fm?v$y{pOciR-&V3dz!a`PMEz)S=0ih`L!MpI<4j8HDi3Z*{g'
    'RTEucjAIkA3<ty_;~0Cz`knmPx5*dZ#hD(6RkcEuUln&M*ipkXm+kvP8NE}PPXE;V7+Xi#I(D>lMI(#hAdVra#-g){mCB<%V+kMY'
    'TozM4nrz2(WhCaA<g;WoFIJf+`*l>-lb)qk%#*%D_Pd}6_aMf=SbO9cGK`>J)js+ZXCS|cWL54y^0UcfyUDZO3-eTWWYX|BZk<2>'
    '51+MEjtzV?b<Gg>h4BkwQ2r~%^7t&KD%Mvl_Ab|$7?o63g}-k+X=a(G!ZO5IyGqVv3v9Up9EE-SHkewMl+K~Ku^4)Bes-v@IxNnU'
    '%qfZAm*~f_!0bCZvhSeJU?MKo;EXN@t8>}RCR>X0m3^k<**`3^h1F=G$MB5n<(zEcEn>A^9X1!3Kl_}F%|&aG?+3a5&U}FA?A>*~'
    'o_V}fnqfeRFJa6p(Shf&X3t1BlYgYd0*m$_yY|X+`!VQE^r_~^p0GJ^|CVr;%5xFhXjsp!%OBY<bv+O_yF}TpjG>o3`*2?i-jl>t'
    'Cp^EsNi#cnN&K7Qnu?z9jO`II4uel}S~zvNPF%h{SgXu)Q6|LFUkv`pdcYY>aKCmw2gc8-f(54Yb5~i7dPVZ0c&r>(Sez$Q<g*-i'
    'KbE=P;&CQ2wQP*VGOc)Dv2JCp=m3lj9#@i~O<)-L8KRs~!s3yy7FKk0!swBT$v?_DvOhfE=nVF1j2CUQY}_}A<>&8mKOS=|^$=~D'
    'Gh=`0t{1y-|Al9ybrWHlBVtiS40dWg?gb1V7-O-If$Hx$R1*V!bg(^O&TM{5<th$tv+J|`u5#B>zCwfWD)4)?mU92#T%8MY8T)kH'
    'JhLu=UXUAT{G|N1%w-6_nlZPqTt}H+qA>@V`?7XB_J!xsBE^S6Tov5aEn}Y-cDu>)g&Fo2j1O@vJJm82ey8}nGuAJ{d+5WVqYnr6'
    '%sabycQ_VT;+l8JT;mB`Xa1~qq>qvIB{}}6EdK5W-97m57dSf~{i<K}Z#BY<pd57PwuT)Z`skD2jPEO6zv;r7qA%_>H`kt{eY^?G'
    '?Hpul75s3JpMxMWtVg(d`7FWuU=?%&2n&331@~K#zO`b5mip}@)uv^(hgh?;J;ZgNs83MsMTXHT!*@r@Gn!OybNTu^3BO%7_J(+W'
    '|JDFMMfqMp_I>$S!Csukc7!=TQTHd~c=`SL^0|_^ZqZ4DVnxWRJS&Z}@qGL@k&kzHK3@9z=zCypr8+R?B3BQ0-Wfd}Cyxt1F&31('
    'FWU<ag|Qg$cd$~Q>@mcUs<DM4|5oGyU%*}%?d&_@EUE?T%41GNF+eLeE<VL0OPHXF{OX*~ZhezJfyk$J21P!y!~wh{{!G#51T(=m'
    'VUHJ$L$xno0@V&HjB5(neqgc9<nt6OFL*x6n&d8{pPjN}ipEW{)<Ik!#`l?CDvW=_`I2XrY84osi0}}}Sx&_i6}vH$+sMStge|^6'
    'ykAWD39z;5s2>Z@9bo~AV{bEwHL(+x>7I%&dw@Sl$Ny@C!$iHA+>dnJj&<JPITrZ0h|B&0OI*?o2<_-NBEE%Hvz$+YSj4~%ASNzk'
    '*m97)8uM0-E~~4DGg418#G!7q+DTm-)^<?GfOZRc0jS%82lMoiKj5avtIAMk^@--qqd2n7aC~he=3||XX1bY~i^vt=Sms!(DOend'
    'opw(CA=zA?aR&6`A$8_KTQ6<9CHNDc?2cKUeNMqQ^l~g`VGb9ExMHPNfYqd7jHhKxr#AdC?GD)S`l@|p_C}NHKF$osAbrF~*g3H-'
    'y+RCJfxhiEt*bTYRjpRCXBKvPnp3S`P573uPmggJU(ex)m?gt~lC4PgQo`6c5m<jAvn+m>IL3kO`R<mT7qeC<yH#2Bm*WyjbK9l('
    'kWx$qTeoNGI^c9q{LCkHm^WlXjP9s2=<HxVWY@(!Ch{ks{U_O!851CU=5byb+2Crh*YBL6n{d3jyAnKYY{c;io)XH{z!@c+AY!m7'
    'pNxK8@Nl1F!e8JW3y~WHYm_mj33`-bhIH3EjT<~OraRwGuqv5OQjc*VIot)$MZQ~`%TEv4&A?wloHpz1kl>n`{g|!||BKEzv%_S!'
    'F~pWHZyf7g(bp<=Pd#t>-`73}oASvyM^-U~FM?qPQD<V_5p%Gm-!IEw6=O9X&N)Q;dH568HNVdsFT(1msOuPEnR)&m>*=ZU261JW'
    'vMb1Ayhc~#s^2AZ9j~t@wo--Rk$3UnHcNx&9R0n^yXb*`i1zrW_lI#JseAUs^&YFIXZJJ$zs!ztTuWlEeA*E9chab&^wno~wZprE'
    'qECR>hXh}iKC|z~4cYtHX{N$z){xPeaR5YTi?g0tEvgkqyYO7Lu0?s3EIvYDn+CV%=IPcLiEeR(XJniN67N=mJ1E4B6tVa!80NoH'
    '<~m>lX?Pat9HjQMamX;_QEirpi*W4zfovP<uJefuq<jR)TC8Oe-C3}^>z3!L$mT&@V1i?lc!^C?`+bdE<keyw2>+7(8ws2a$C`3K'
    'sRW}@h!=SmSRwQc@$S<ZXlAi0pW=Nc9J{(n>J%E8&s{{#(NWe<FgbzoVZ=FMtp4a_F?q!}l|0U;ox%B_UDP(%yJObf;;ZKv$GPG-'
    'Xuo0y$O_M~K+HaEK03?4fHQeKw+`%!&N`$rjIgN9<Ld^x!r!B8K^?iOvb(b&{P!34|M4CBuf-*DKeMpQ=O560tQM9!2MJ6Yc51ya'
    'R^7i)XL9VL?_j4^<Rutn@Q#Cx;LAc=ErX|Fb|2bM=o1H@+G85=^bw~V+E|U}uV5xwESvF{5pI^BqyA^_iv;IZQj^JR`LN?RuiZrU'
    'Z;-=nwf<GbOMmi?P%@9h*=p3dok}u+*Jj>XH@F}2-F$uTe~FD*gm+Wq_uq84K76n>kQI}#U9m4at}vhK&tdq#gopcOykZH~^4IE*'
    'sUB*^W8Q>smv*JBBT=wU5~ECYFB0oiz*UgMxv_?;%qQP)K7w?NKjEWDV&wU}B;(N(xrE1c&b1GIj^!PMy^BFUGW$4%*%0%`9NQvT'
    'cE+058GP&CjH+Mt&L|gFJ3N~<oJoD_HIZY+E6xQ>BBNhD$uah0AGts;y=UvNPGOaju?n5(RH!zqK-PIb7Lx|X=wjHv@9-Rq|J*R9'
    '1^-`jdnTaR4dS9=gYp`9Pgm5L9(gglc-H?>R9|efT5!Ro2X-3j6zZ5A5l1L;NN_Ao+8+_IdExhko2UKKd2Jfo*T6d_>sriCO||ae'
    'ue!P+e2l_cP0nO~B3{3F0o%PPI(_pyi(IY_b?7|ue1qZ_ArAn>>M9EMa>Hv8HxshIF=q0V!E4q~=Z7fUxf~)t2|2pdP7oB6Qn+Dx'
    '%=Cb|H;v0gpOo^77z-mljZExw4ff<ZgEvI(A{KMW<i$j-JJo7{tzDX9W1JYQ?n`i*lypl#{}RtV;|<!%_3v{Q;&S$T!B;y=_{EZ+'
    'QOCIX<q>ZXc4}sEYQmtw|5dp@zja?{nwHN+DEs_E+?PkTCbn*@OY&Ixd`nr*UdTAkCZ6P#lXFR3^DO4e=I#b|xudw?yE}zv2gK8c'
    'XP~&#T@ot=pE$`u^$NN{Bx4FQ9U9qpc#T{cR`rN+YOraxf;R^{;g-a}ExV-;Sba2d3#7W--@%7Hp?`*PeV@2DMYj^_9vzGbcLIJq'
    '=jH8I5u?ZSedaxMX0YC$Fd4f6azR{}?`UFv|Lmvh+V6t@Q@k5Kzg<*EC-C7vmavxT?kG%VpkHLQS*Hx*(IQ?7{(VueiE)Sy<_j7D'
    '$WiKA>9Klsvd6Hlg76~P&5|>BXX4=W9O8j<1V>8>2XSysW6j4aV@^pNYP@zTERVoBT@u`yoqR8^E6wxUWc$-~Sl8SPE=Y7e`S6>?'
    'cuV5Z;~c2?ZzebSenbX5H@X+yf3iuzUxGO$__-X0Yxv=H!Zhwk>Bv#`zDL}3$#+;j0@qD+HB;tFwMED?;8c0;kMLx)PKU?5T)F3-'
    'J@9RN$g5X?Y0IuR;!Cpc&Ybxf+V(4H|MGZ~Sc9MuEGRBW-F`u*>x9GObLKTFm$T^n!eVtU_&D&+Opb|jjenqREn{&G)s98(GsVH!'
    'x+OVKiiZii0N&3yrZfEN@Uv>B3sF*+VH#;H+o!lb#1Tdz+>eOyilY6Uu?evbqFPYTt8{;$ykAx6D5B)O3ouZ!Ym$o9!#nC#YGA`&'
    '3Ob5#+|!P6)Ofe_9F_u8oWn=Xg8ccfpIsjRgFC%1`u(55Q|0hv1@$21@tG*3TymA{ln-A&=H}^4%6)ptt5@({u^vvjkEGW3eB*i-'
    '>}r3N!>UCZ<ICtIU1pq$g8eLr{p9g<F6Z#~xa@>;t*(oy6`%2DS$zRJf1Ee42%mWsHr*Gn2qkx_2+OZvXUgB5u2;+GqLLarS<43F'
    'DaN3c=&1+KEasyrA9wNRzp{=j7XD4a1Rt^;PE+<`-abNkj@)2cui$s6!``Y|rVBIjwwY^*PcXrz1^Zsu2i~pg6LvPiE`DYg3hoZp'
    '5v0m_!W6$L_s(aXaVpsg4(Qin2N|pbVwf186vj>9_kvp@6-OxH$autQmelnlHkS6ZM!gt%?ai5Y>|(Y8<5XrmVlvMG@}!N82*N+?'
    'Z+q3omN>3E(GffJO8$@O0rTJQ%lj$DHS9ZnL^0s!eRVjkf2SB{70%YZr41?;te*7`I14}e)!_wnWTF54+8Le*lMQn14emCqquhg+'
    '82OQhKVR^C!CJorgUaxIbA6c)5Tkf=u~!849C_Z~z0M|h-JJ~ZzgbU&=R!^|S}Tt4I;y!Cip5~uMEO~Ydnxs-0(?zM&wf%9hgg@&'
    'HDoag=D+zMzhPfduHPjNB~ZF0CjRyjF*3;chxRy&P3T}-fe)0rH(=*;J_53b()Nnzp}_lCWO=!j8W7@AD#lx8F)b<HsRUD1fRmPZ'
    '^DorE71<jNitC_HpT-#{d>m=}A<V=xw!{t2)}a1-CO1m{wdhsi-S!*aJ4RzRD&3zW#%LMVTln9EPd{huT9KFf;5?1?EW9EYJN9Iu'
    '-Uu!|*Tyb&6uVfaum*(F$c`<u$7#Hj(sA*F<3X}qBFw)Ox$7k7f6m5K@LYr3LVKeuPJ@^lu%#&{!(*Hv7a2zBK=~`DdlWVf*MGdu'
    'igUc_hUhGnlIex@PRaSoc1KHW*AD*euNl4&_OFV(${U056ca7rbz#Yx7S}E$IwyH&`p(liV0k;@fr<>`_CR^TdZ36{@i-9JyENXe'
    '{(CPzVGom?cgyhJlHTZYjM(U$@PkW?Qy$0F=FbBAQW-O=0bpJF&ZuipzpAw<Ui(<iYhR3ARBDAO&&@C`Ce5F?wA?vzG!gfExQICS'
    'P%|CZ>;;FPeuXf=nV2ZmAB(d<eSAPZoIy?;V4qm$%z`erSzgc;@!v4M)vTP7@ioT#B|qy_sMl4A>`I=Abrghei!?lkux{PPG(0t?'
    'E%U|EhF#l?){|MW4FmTO&SQjrX|86zh-<dA6Y9H8Jm#5sD?CpP4f|$bN8n6tcM&gCu6t(2eh?g{3>!kYLxw}7_`;vXAST?FKUo*G'
    '1k+cPhso5vDz*)elQxgUyD0F0y-E4_Id*=Z<50w|!?wYBaZB;CN5+S$9g|)mnY<A3!O9*IUpz0UqmoX`2{r-aaM&*gc{G3UI0xhH'
    'T2(RD$nx|e9+>Zdn~m$ABG;*l&djJA1gA7|0`tzwyuVw8@K9UX&!<hF0ezNq;w4_sHrR}#Ow0xKjDt8(GvwUWERV{#OwNL9Mq<r4'
    '4^4*4f$@}y8UoIdR>*;p#trZ;w1}UQenZIbI@*0j*oQ)#0guZO=bw}zrh%O!w>;;aa1je$wF;X{xjj<QNjN{(f;&UG41rfjID*J$'
    '$j>RwgD%dNE$fET-$^)&vH!(ibH}6DYHni{H!V9MPlVr`u05grMb4JX)&F4+F6MJr)Acf?otJqnXd2)6=<^SIOwj!h=S#*p+4&Ow'
    '`XkKdp){AI#0i~>y(Mmj?D|mNR-8#0f2K1Dda4);8fnG#ubrWem|(=SXXM{k<X%dC65nK%jT4{Aaaq`f_m^r9QrLGE$L9Sz=)UnD'
    '3?S#Jp0U1tAYUJ0-<b{gslB6cmz36!aQ&I)#CcqQQj+(5oiRH)&!<9I0qTW>@`m>pU>xuneS<tFW%k`83<2j$_$&_d#k!jEHNl!F'
    'mufQq|5}sMd6lin*J4nk4AwjqYszrNe#V>6;zp_rRPIy;5B{)jB-J;xxxtvug>oX2yIsa_u7jzk4=SVYATPll(W~eyEIXrb!+ZT='
    'z1P&*%_MGg3qKwEV>}Fx#ZCxs{DS90#kv>QyL9PuDGrX!FYQ&rgV)aS;2qMr>Kvc%qrKZ9J_>bqS+AGEJ^*chi@2WuqJ5kY$ISHd'
    'L9xX5r(KCJnSEzY4|ea@yGK3XSj~^X02Pd>ws@cEgXemFOz$)%_+H~AFwz(&#OESbCvQVizD@KFrS<Mne?{y8M(cPei3iH=*9re~'
    'zU%xbg(Lit?tjrH9m8!`sVh@Ge1u&spM!Qng<<!}ubUo|{tBw@-N~FMVXYb7$tElToWEll_e1yW(;huvJwv=V4D6S^?awiGHabzg'
    'E5<hGE!Lm0sqa=5Bc#1j&JOs2J2_Xdr!w-OG`20zPMcw(;p{|<iB9pbzC*Pf5#mzCcrYFTGBq8uzFjt5t@a@>tN89;*=xcW24PO`'
    'u^L#kIUnqC(x*!48~8}aDZNy)pPN4D0g~<Mk>mgvKJ%^x${z9FmyKjC=l;j4GLrFkaj&eVZ(;4H2Y%Ck)1JZldNRHwdHZA8L4KdX'
    'TN}KOL@I{N?<Lg?U_aJHY#)^x+WfwCL_Qqz%%^=nruZkvL2t+(W&0)Hb*8?=&B!m-MJahCxJnpqRK81KN15JIa~Hohe~$I%K6q)L'
    'o_3Bm{L6iMSnoZu<%N&=upgSuV+U9V>?VB3Tt-qo80tX8iEI<>nJxWjITzEOOf!9Lg#Rn}E*a0k13mh+emcAI+KKI!#c}Mj#F!#h'
    'Hu&TC*yUW`f$w%(z&(X~fPJZt{<9X0Gd#!(MPGcW=MMHz?Tq&??}H2LtCQ-%a|K-+@t^I5t{qG_7woAcV$FT9vHa%)i>JJw0*2wR'
    'PSg+CvF|VMt;?_W;Q0j`OsR>=^6;i)a!DQ1XR=wI;iMj0#AWUe&&YIv_I7c8261(Qi<)yrGfr#eo*s!a0elD+FB0`k?5t7jEECV+'
    '{p>LQxK`{<X4^2mUU*+cf44{Wb&(7wj1}@Lm)nlPYlys0$=VCM1n$R$YMADuGwKumtehV}eL!v^{*mY}r*inf9@7@pH&{Pb?U3n*'
    '%JuL{KilkyFKKcSeR1hoEWRiD;f04k-v0`8wUR$i^5Ri2oX#$TruC0k#POhBzGFYU2-iXMHU6f~`L$yoxn9**&rdK1cy{q!;p<V1'
    'H@9x}Q-7lU9e-qBn5n40LA#RMp8|twHMh=kegc_|edStcyD}bOxu=88-!#6H>T8kDG}n=DW4%N!9>Sj#@f35MAJ%Lkua)R66N_9s'
    '_8=LZ86PtE&GZ@Si&Me+G0}@e@+IFuUlH%cXj8-moA53Vv99TTN!+jY){C*n>5%ejS)ZfmE-L)Yd<+}PGt)DPp8(Epy3bW&<MX--'
    '#kNs$tZBPH<ria)Ey+3lQt#}7d@S+ZW%)bv*u!MbTvn?bOlhp3<co+_FQML;o5pC;GG<fV7)&*zZ`+NjGs)Zaf^)mbx99S?<V-Vs'
    '&SH{q_fwx=*0*7g{S}j(Nto?_sPd3!xwe0?pBKY_^n>K=iM@t<dV{g;DKAtnw$%zh+pHny%FRK{J>%^CR)#;7*nG^NREju|vv}cB'
    '4CEAZ{<aqNCo|m~x1xrl+tab#U5{qIIgQ{>;XUP?*_i+1T%U;3=QXoo(tiW_V;F{A-M<I*^k`Ef&jt2t@VBg|J<B6ydjY7tZ=yEB'
    'yVcBD)P0>5am9~H^=gI>@eB7ls2gJKi{)IpzgcqMmG4PAcnq?~2OAvDoN~U3Yu+x%FOcH7o9o&Ud>=o@X~=oTNY{4cI|}ke>3;XJ'
    '|1`>);&T}zc1Dc9^sF%srDW}%^<vqJb7no`@Gcu!SzNGhl*d~TmoddPzLlMeq&`mc_T9$T?j*R~7>>}<u%2vUbx!Itc|OTU{6>WR'
    '9#O85zkBnr#x9TRe%LR(p|9ekj!*VFZZE)(5WH;c9qUPb|5oKa&3791C+y|?BXJ&z{3FK0CGQ0IS@#FrzDaJVoX_w(i^s|F!~7c`'
    'um|kt$=Sl6XKd{4y*I%)j7!{7tHf>*J?&2lZ=vklQpzO~b@f&79BjJR2J4fs+1QonC-`NUL*G&#4Z4f6Hv9gxZ~6?QMfKYZ0~Rz!'
    '3AYT@G8|c*)Ry(mteAJ!JLt=DXKK%e&trQyE$XlHWx1Wgd@)X(1d}S(f4o9p4)o}z2RhEe_2?~vf?n`pZ&LpUatrgbS%z6I%eSiY'
    '>rO-WHCO-BvCsc4XHk7`GcvLm!5;Qa1{;xZ0ypw|Vyf8#z0AJ1`Btujj<8Oczo-ZOnE5xV%$?u&PY>2!z2^t(`Dyc_@Nt&bXUn=p'
    'uzMrFF$;0Mi{j<KWIKKNj)2dg+D}Zki}U6PUW1JNg!z-U;CsyWGAYbGm)f`t_gOzn9xEXWbOXlJJuEo)O0zgFQ25#Y4$m6crEu=3'
    '55e^BKc7~Fb89%0*{M67*{#XUT-){#Y!ag}*6bI%S>L1V=dus`fxIWYCam8O$V*uR2s+>=*+Qm&06Xf0*w)45fqV=zGOR6eE$32h'
    '4fX7W_GA_slds7z9yi>iY}zmRSF#2nsHwI$+?gx(CZT>P$}<sPx)c2g#rFz)DfN7*-xob~$bRxFrvu~d&f8K0_!<5Io2r+s7v%N~'
    '#gyec@5MFEf>T#;rHFpy%5yTmWB8!5+Q4MYgxkB8oKHGSa9;F0pKi)tB8(&17i7l@tdf29kO!;H{B0Ne=9%0dx|MJM3ocvP6Lez~'
    '+s}mAKZyN*b+Yz!Sh$WX&ZpR?rT86HAJmAKeHD-Ps4v8Nvswfj`z(AHHtt%HY55vc^lPHCKc5wFCKuYp_+G?%@-^FXI}>qxCg!dX'
    'D-;#jv&#A8`<s(<T-FxzQ3&2!agW!?<>>{R&#+Eqc1>)B$@{=APR7^KR2xpjp7!8di(Y?%|A)s*8U78||AEgZIi-j{nCec4Apb^6'
    'A4l0Q24&mVWLY${M;gdpeQ<otgU$N6fP6(C;TP67h1Ej8LO!F!4&JUhyypqCO|}`Hr>g5H{9%MYot;176D;Npa0chetk$09@f@ms'
    '^7qFR(7&nV?V?gY0nQYQ*%&B)Lf%7=zV}kjFZ45KE35LrJbrsIwFAQ{Tj1+8W6tqSy*N}I!0hFX<oPbHA<Wsv&dBb*z<PHI^=2+7'
    'NEjKMa~`iCdd=}%vyA<v>OUKOtWR3Sr|pXJw`toqhj}UNU-xVFnRRP4{rUALi_vyJkaK}^<i6TX%3p(gfIHD4uDqy#m*TQOPArxK'
    'D5$OBb{}#Do8vw539KAES6~ZGWSkD?&am(fVXif_X{`>`ouqgbIi59DXQR|SW@}oMekvT__^g*<8?*J6tPcizrn0_D-N)m;VroyW'
    'v>io!Q1w)eaX+@77Wh2mIsWXqf-`EeDd=I5!kqD#?`5OnyhIP9OinPPm&ADfi}cd&B<qh*7m3<2>Y+@0D1u9f<Vhma1LEL4^E_ZP'
    ';q5JzDM2X*J?G>r(^(iBTjKAqM|AsIdk{Z3A_v0iS^v5$3I2fZlB#DxdCblm$Y91<%y>XQktq$dZEl!bcAFX5L^<`Mb(FDtnRo2Z'
    'v-rG5Rp}p_aGzAR;4jd)w%M^1t|#bB*stU3{B!+Zkk_W%2jVz$7>&q2{}nP=?OTC<k+{!=HAfw#zID1UkqOCXezC^$>^lu+hko8G'
    '?aTK!RSym}H|za3HnQ9unHudo+U@Cc^r!dsU%&m^Z_C5s_|HSM^xlsDT<?Fz$A3TEe*2H#K#Q4gV4<T$IhxmMSZRZ&ZN{>Rn_+8q'
    '9^C4u$D@Y-V}&WZH4HsaMNKn6CT>K6@l(aSr84wBJi~|tN=$Z5pzgM2ups7r*0q9nM?Nj*{!Oe>e{<j&((&);&99UUCm{lyK~G3R'
    'JW0)%XQN{IO!@g4^M*j#BvmG?n-+PbpoJr>WV=~Wjk>b-+BJN}55Hp8)*V&>Owp!^ws+d2pS=mO0`;1l4K=-XHCFXJW0ntNR%Vqc'
    'AnArw@zA36k=ZmDgQ$$sTtd8)C3wTk5ss73_dJS?52^qOSw&mQLRHw%WJfLa_ictOd!2N<Dne7RGo{CXRaHK*;P_;*;~GTF${}Qk'
    'U@)DfE7!5otJ7FBMg*;>dTN4}*Ags#wEUN-op`i{p=dH4?_0(MtM|O!P%`4ZAv)`3NXf#!XBK-}xZe}~AUi@dRrY#h%lg4lS1`X$'
    'D40x%RT;*D)$*aj%tNf5h&IeHbLP4!XPD*Q1%p1fn8aCVt||sqDvens?mmME0qGLm&{E-*0jXQhnH~%)3_q*t)|QO*J7LRjs~r_c'
    'vmcOY7ugs1eSfsC!7Le@sN93K>Hd^^(R#G*sj=a`7g>14>l5gy!ip_*4ME$Qx38`rp4~SS*SxmFs_o&leo1#u^}(9<BmY?!&z~Wa'
    '2cnu6lPy)Kdw2c2wIg;UWY4|#scQkDH})&Wx<H+M#))OFur=~(F0xSTpn1jlqbv<E18@)cVC^!DuFCzzeP&%(iLEWqGOu_AEFwV>'
    'us}JdJ;A)i<d+`#?N)|yl(8<p3KoZSw=z*tiyc<ipi!|)-r7ndKUlR|P>6n!m28;`YW|(gp_xUaPgqCe{v5k7oX8?$I;U~+iP4Ut'
    ';@l&{C=FIS5K0rP(>IgZn6u?IK1k+?ZdVzPiB<I?>Pu7+N>&_Jl^qmRS5h~U!U{4rX6!iEY#G+GRT_Q3ZlF#DJO3EB<XxAI6^-{)'
    'RSaVxYdH|z0g`UQUe=Oj75O>KqhG*m$t`Myjk0!G-V|2(^zWp#RX!iy-I^iUz-j?q#G-&W2GfJP1J+c)?S?EmF<cQNGOc5(8adqo'
    'r14Daiu1{z6GV_x1@9EuWh2fm+d{p?*eN(-Q@lr&N58YPgdUZtqh4g)6TnuwWU7uQB4fn%S?xU14;n8S=0f4wM~uCnbsbuEF#GYO'
    'bo?OnRO&r~F%FrKU>^<&iZd%mRfLl4f}E~$M(dY%6X)lSbUe%fqm^H%#^u&Ac90lvkqz`wN5KTu{D<BpWrSd`V^zS&Xk5;&%Firz'
    '<XOY|+_0mhTJb-Fal2w)6S>?SQ)jzq%e`f3J4yr|R@6~tzZt@Mb7q^T0(MBg#sy<jq7Nun1JwV$yqrlR*06%NAbKvk^L_Fh$tKpD'
    '6lWVU)p_Sk^;#LSLv|!{O(PO_x~R*`M2S``WVbtHuBYq_^9``eN`>wcucX87gdi`76+_W=ZIpWn0>59_!BQ|4gMCA+zFtWsKVwK&'
    '_e5c{%%Ag21vqv5E$ecT%!5_Wl-vO|^3)rBA^S+^gWUYe_DCY_WaW0VxDr0)ZxmHveRjVdKJS8^cX&m*ma$dUGcgd^laD0&l#Qr9'
    'm1eF;)*wovKyDN<J$tGgnbZ&weejx_LvK?5VLi9>hm57gI=ieh5_KA25xT|+?<ndYWRA|Uek&}?eWk;JV#DFt(l9!(Ks^QHB>%}F'
    ')<9(QJrv#v#a79#O{Uv7>SVHC{=odRUD3cc$Ii*3yOCNsqxv68_g>Ju#PBnbk+<!t`FPLsXZwn0g?CV6?5ezy4RvJxY@|A_DW5OP'
    'x;~J9*=}xA%(znJM4Clwg`HGCk!@LD_`$yNZry1X-ei9t#1{V0U4Pt>F4ZwEcfKihpmglxu_T6;O(LN(I>w@*tAP7PiL5wh5rWFv'
    'rx<~geNOf!t+Umt#zMPa=}JD!>-*+5TRq8`lP1U(QQxP|SJGkeP}Ip;M74=ACB!p<)n(vowl}Hy2|1aJo3rD?oXO?{eX|7n8GV7}'
    '?J4-8&!No2;_@_kr*e-(C17e@Qe6bn44=gaQHCB%?rO3BMEa}O)M|rf{RcAMCu79_*Wu^kFWD%$JF3i4$-V`yGp<q<9le|B@t0}+'
    'Y?Yxlvin><m+Q-Oee?RPrN8rh0e`CX^y~A<bc_sBRk|nP&)^@w<44HK*Pr5h*qpGUu28nn*)GXiJ=nLBu`@g9!5TgKUjA%83E5P{'
    'xU{iSmC6r4e|R`vhQ!Im0a9Hi)A79`U3Dl&IOXN*;|@uGs2iy0ekg4)))}r*TUBR8u|qDC5d}lOkSed0Y?WDIesm2xoMbw0K9zUt'
    '8Kv21v07bJb3O27vaDOocKhseoLMWwHkX_Mj@%@9n_<-Aj7|K`6*D{)q1hgOFT-3m1-l3A|C*>EW<C)yVjNcO3$h%c4{=JWOounh'
    '!*mAUz#fGC@bPXFi!Ei9V*5xoSca9Je@8I8BH~qN?5=i|Iw;GIAPu&DK|@poA&TopjP<d3$L?Rm*cnHG&ti=^R!_#vltTFA*1JIW'
    'NnfR4?{i(&dK1Y6mM~3~qT~v7UA}W$6T4`P#hGWnuV6l^v3DH{?wwCve=_suRVOS)m+s*8qf}SqZPxVJV^!jK#udF$zAl+=a-odH'
    '^mnWiNADMPia`2_+y@^I+IHp}W?f_I&Ye3e+^)qK$_){ci+T6xDqW&%yF19m>=JelX|pvq|B@NaV7K1?GY&RCm#1LAJN{GCwAz1q'
    '!Rdy-_!-kr|MRfjpZ5RxGuUiT$N%*9@nL!5*-tnltPdCO35QXY$`*MCu@{)W0&g5FmkXQ%#7#4ahBa~%UBwBI1cVtA?-||%m-R~3'
    'DSEs)Oj-1TM+=yCWPB*|EAe5zO$6pSVt5RSkRrFOeS*)Oc~psKPdT3x_Du$9=+E`DcR%)EW$1Ld9oVHNWvJNq1Ik$4Sfp@>(Z?Cf'
    '_~-|>+7*&p@^yGS%({VB!cO{VbZh7yd6)LBzu5=K)tAbw<}$IhaG})vsXdvnk21>~T<@^Uy>S?s)7E&35>{j@m6MzB3L>vV+dM7e'
    '@%ANXFkZOM;5<T1gvfS+q{9fX!02SNIfH5a(o6az?5#3B!jgC4=@gkH-uFvlgg~1-If&_teZ(6fH$m~c5-w5RI})+Ndf>KO-;!*1'
    '4SAZ|jJI~ntn|CAOFb=|?HVH)ZgsqWowhFUt^?Lku#7WhR>)$Iy-3LdVQ0C=>WMMqgj)Qxunpqb1c@N6kP&7$W*NQ$*dM~o-57^0'
    '&;B6qA$;x!la58-6B15f;NUq$pX*1)2|1qo@i=f;Z&_~fiN2A!@nUBF3}>F>25axIu6MMM5L1fxm;e7;rjC)_ms@ea2=RN)net8E'
    'p-pkW9PxQpPx$E=57aBBI;4I|G;hX<tC1wMjZDwjt(e16tY4bPD%}gin_sa8f9-do3(tanU*~F*J{@BPy>Xly<H;Ug!PCb6uSGSI'
    'I>-~y2*`g8-zWUcBAA)o##qxEV$8^&3}<BjR?WZLb8L))tr^GkmaW4iGI~X|gdIK>+tA*S6Os1tM7>A`wkG<U+#KGY0DFh<9z9~5'
    'u}hd%<bBv2<l5Y1A5p~A5cjMi+xgvjQtEg0EsscSS77;g#Mz;56E4c9%`CQ=EXQ}%<$KiU3jOdM$H-77co#?`f|VA5oEYB|)W(c5'
    'd_HnYOa7DwW!_MKh%64{_@T3V<UPSz4<Q)8khKLoB2;%H`V1<1r)bYVDDn=nsOVmioDg?RKT!rO)#t5!I-uu-xKP9)udojXA%~0`'
    'Vm?=KE#kN{jDjLZ#ocSmvq`dt^DMJ-KG}->In)2Czs4Blr1*Ijn|e|3t}#Z}F|vr9qbV7l%K8rvZ!wP=@ps|az#c%}B(Q>_Z*DHj'
    '!{>>2D5MB1m**DmdCQ)uL`}FyN&Pj*L&)6cg1ulEaDh}x^&0G0LGRf(^c<IJjNtvAcRP4J^Lp<EThDDC4^C(ByVDF&2W8$hT+uje'
    't>_MlwK!n?7_S>tdT@rkpC}(2ud$>#maLIHchu86(dRt7jeS$Z+6k|Y+ch<~57(npF@Ca0eF3Hy?`e~9*QcM&BM13?z$oy2=^QZP'
    'qMn!3S`=m$WAlJ>o$W9(7oFT0_a;CljveY<Pd3{d*Kg}d?K`crqmfrc$e6q=06pt+?swz-a--T!$+M1L3#(%jh#33HOL{MfdrZ1O'
    '@cAb?i_i|7AD_+~Wz8q^n&8o+d+1aM{c$Gr4|3php7Zsj@dM;9&vMhV=-+Uj*0i53w>zF)TeB+HQ%P?;{vC?$9LTcg_Q}KN+(L18'
    'uy0&q(@g58l6j{&Lmupp4c^vUry+2xtXI!O9T#SsPE0>J+IQ-Cva`|VmzZY-QKWJ`VBb=d_hQc!uWx{QVuy$W@*Jfvpl9@tj&%YD'
    'hOSHY6unEzoV4j|VQ-~(?2RgrIbP*Q@*dqBAm@;@!w?g`vk$~qPqk#U7szGx4zhxIxpPhOuHzkDQnXq66zDI=$irWuf0o44DEyiH'
    '{c@>B1hYpQst-V03hszbatpjs&hfY}v@d!6uB_Gl8^>8(BPZ?|@kNRErTMQpY6`q^v<V4K#^;CifHyb?!cI!fCG}m7ZY{I3(^z?C'
    'w>TAyaE#GDVv$Df<CLr;pGTPO={cT~orwNPh<71?yKrRaLd@`);K$513@J>t0r)P4R(U^y{Ka!vqaI$$cPToZsks4J$Z8!Dlo>rM'
    ';xdfh=TXfA@~RM$2X(c`5Etx8jrUTes15R3fKSMfZ#_avMO}u<(fKnjTu+BRFe4d9<*hMH(8*8xw9i{pe<%GcCG+(z`fbf`n_!9Z'
    '_eR`d=-VMD9FF0T8bf5{qh1*FVLlVqbx5Q%Jy%61seb=%aGoU`tSuS8n3-qSWPFzed{If9!!}aydbLk!ls0lxM2#BADfDMb{ZjO6'
    '%fDAUuPVj`=2y_yo{bS~fQ#JY-M}d8ah%zg28@T>7Mn-eTowZ`S)a$(2}9p4(|R%xG6sHM6u)@%e0C0>^*<5UD0_Z+tzK%qL(o&L'
    '0@QfEmXzcR@2P~mdik?Sz3KSx%VR9Rv>v}6d-)%}9@#k1!*{T8yw3l4e5f?rQm{^$UZC>34%U(U-~R_BA`)l'
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


def apply(root, backup_parent, files=FILES, downloader=download, verifier=None):
    root = root.resolve()
    if not (root / 'manage.py').is_file():
        raise ValueError('open PowerShell in the project folder containing manage.py')
    if verifier:
        verifier(root)
    verify_prerequisites(root)
    states = inspect(root, files)
    pending = [name for name, (_, current_hash) in states.items() if current_hash != files[name][1]]
    if not pending:
        print('Photo admin update already present. No files changed.')
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
    if verifier:
        verifier(root)
    verify_prerequisites(root)
    if inspect(root, files) != states:
        raise ValueError('local files changed during download; nothing installed')
    backup = backup_parent / ('EK_code_backup_photo_admin_' + datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
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


def verify_columns(rows):
    # Exact reviewed local layout; stop rather than guess about a changed schema.
    expected = {
        'id': 'bigint(20)', 'title': 'varchar(255)', 'info_type': 'varchar(20)',
        'description': 'longtext', 'thumbnail_url': 'varchar(200)',
        'order': 'int(10) unsigned', 'created_at': 'datetime(6)',
        'city_id': 'bigint(20)', 'is_published': 'tinyint(1)',
        'photo_credit': 'varchar(500)', 'photo_license': 'varchar(100)',
        'photo_license_url': 'varchar(1000)', 'photo_source_url': 'varchar(1000)',
    }
    found = {row[0]: row for row in rows}
    if len(rows) != len(expected) or set(found) != set(expected):
        raise ValueError('City Information database columns differ from the reviewed layout; nothing installed.')
    for name, kind in expected.items():
        row = found[name]
        if str(row[1]).casefold() != kind or str(row[2]).upper() != 'NO':
            raise ValueError('City Information column differs from reviewed layout: ' + name)
    if 'auto_increment' not in str(found['id'][5]).casefold():
        raise ValueError('City Information ID is not auto-incrementing; nothing installed.')


def verify_database(root):
    if not (root / 'mysite' / 'settings.py').is_file():
        raise ValueError('Project settings not found; nothing installed.')
    sys.path.insert(0, str(root))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
    if os.environ['DJANGO_SETTINGS_MODULE'] != 'mysite.settings':
        raise ValueError('Unexpected Django settings; nothing installed.')
    import django
    django.setup()
    from django.db import connection
    settings = connection.settings_dict
    host = str(settings.get('HOST') or '').strip().casefold()
    if (connection.vendor != 'mysql' or str(settings.get('NAME', '')).casefold() != 'exploreanywhere'
            or host not in ('', 'localhost', '127.0.0.1', '::1')):
        raise ValueError('Expected local MySQL/MariaDB exploreanywhere; nothing installed.')
    with connection.cursor() as cursor:
        cursor.execute('SHOW COLUMNS FROM `explore_city_information`')
        verify_columns(cursor.fetchall())


def main():
    print('This hides license inputs in Places and City Information administration.')
    print('Installation changes code only; it does not run migrations or change the database or media.')
    print('Replacing a photo in admin will clear the old photo license and license URL.')
    print('Stop the Django server first. A backup of replaced files will be created in your user folder.')
    answer = input('Type APPLY PHOTO ADMIN to continue, or press Enter to cancel: ').strip()
    if answer != 'APPLY PHOTO ADMIN':
        print('Cancelled. No files changed.')
        return
    try:
        apply(Path.cwd(), Path.home(), verifier=verify_database)
    except Exception as exc:
        print('STOPPED:', exc)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
