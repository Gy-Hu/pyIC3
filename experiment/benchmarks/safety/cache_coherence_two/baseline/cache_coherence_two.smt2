(set-option :fp.engine spacer)
(set-logic ALL)
(declare-rel Goal ())
(declare-rel Invariant (Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool))
(declare-var A Bool)
(declare-var B Bool)
(declare-var C Bool)
(declare-var D Bool)
(declare-var E Bool)
(declare-var F Bool)
(declare-var G Bool)
(declare-var H Bool)
(declare-var I Bool)
(declare-var J Bool)
(declare-var K Bool)
(declare-var L Bool)
(declare-var M Bool)
(declare-var N Bool)
(declare-var O Bool)
(declare-var P Bool)
(declare-var Q Bool)
(declare-var R Bool)
(declare-var S Bool)
(declare-var T Bool)
(declare-var U Bool)
(declare-var V Bool)
(declare-var W Bool)
(declare-var X Bool)
(declare-var Y Bool)
(declare-var Z Bool)
(declare-var A1 Bool)
(declare-var B1 Bool)
(declare-var C1 Bool)
(declare-var D1 Bool)
(declare-var E1 Bool)
(declare-var F1 Bool)
(declare-var G1 Bool)
(declare-var H1 Bool)
(declare-var I1 Bool)
(declare-var J1 Bool)
(declare-var K1 Bool)
(declare-var L1 Bool)
(declare-var M1 Bool)
(declare-var N1 Bool)
(declare-var O1 Bool)
(declare-var P1 Bool)
(declare-var Q1 Bool)
(declare-var R1 Bool)
(declare-var S1 Bool)
(declare-var T1 Bool)
(declare-var U1 Bool)
(declare-var V1 Bool)
(declare-var W1 Bool)
(declare-var X1 Bool)
(declare-var Y1 Bool)
(declare-var Z1 Bool)
(declare-var A2 Bool)
(declare-var B2 Bool)
(declare-var C2 Bool)
(declare-var D2 Bool)
(declare-var E2 Bool)
(declare-var F2 Bool)
(declare-var G2 Bool)
(declare-var H2 Bool)
(declare-var I2 Bool)
(declare-var J2 Bool)
(declare-var K2 Bool)
(declare-var L2 Bool)
(declare-var M2 Bool)
(declare-var N2 Bool)
(declare-var O2 Bool)
(declare-var P2 Bool)
(declare-var Q2 Bool)
(declare-var R2 Bool)
(declare-var S2 Bool)
(declare-var T2 Bool)
(declare-var U2 Bool)
(declare-var V2 Bool)
(declare-var W2 Bool)
(declare-var X2 Bool)
(declare-var Y2 Bool)
(declare-var Z2 Bool)
(declare-var A3 Bool)
(declare-var B3 Bool)
(declare-var C3 Bool)
(declare-var D3 Bool)
(declare-var E3 Bool)
(declare-var F3 Bool)
(declare-var G3 Bool)
(declare-var H3 Bool)
(declare-var I3 Bool)
(declare-var J3 Bool)
(declare-var K3 Bool)
(declare-var L3 Bool)
(declare-var M3 Bool)
(declare-var N3 Bool)
(declare-var O3 Bool)
(rule (=> (and (not A)
         B
         (not C)
         D
         (not E)
         (not F)
         (not G)
         (not H)
         (not I)
         (not J)
         (not K)
         (not L)
         (not M)
         (not N)
         (not O)
         (not P)
         (not Q)
         (not R)
         S
         T
         (not U)
         V
         W
         X
         (not Y)
         Z
         (not A1)
         (not B1)
         (not C1)
         (not D1)
         (not E1)
         (not F1)
         G1
         H1
         (not I1)
         J1
         K1
         L1
         (not M1)
         N1
         (not O1)
         (not P1)
         (not Q1))
    (Invariant A
         B
         C
         D
         E
         F
         G
         H
         I
         J
         K
         L
         M
         N
         O
         P
         Q
         R
         S
         T
         U
         V
         W
         X
         Y
         Z
         A1
         B1
         C1
         D1
         E1
         F1
         G1
         H1
         I1
         J1
         K1
         L1
         M1
         N1
         O1
         P1
         Q1)))
(rule (let ((a!1 (and (not E) (not F) (not (and (not G) (not H)))))
      (a!3 (and (not (and G (not H) (not I)))
                (not (and (not G) H (not I)))
                (not (and (not G) H I))
                (not (and E (not F) (not G) (not H) I))
                (not (and (not E) (not F) G (not H) I))))
      (a!6 (and (not (and (not G) (not H))) (not K) (not L)))
      (a!13 (and (not (and G (not H) I)) (not (and (not G) H))))
      (a!14 (and (not (and (not G) (not H) I)) A (not (and G (not H) (not I)))))
      (a!21 (and (not (and (not A) (not B) (not N))) (not A)))
      (a!22 (not (and A (not B) (not G) H (not I))))
      (a!28 (not (and A (not B) (not G) (not H) I)))
      (a!34 (not (and A (not B) G (not H) (not I))))
      (a!35 (not (and A (not B) C (not D) G (not H) (not I))))
      (a!40 (and (not (and (not G) (not H) I)) B (not (and G (not H) (not I)))))
      (a!46 (and (not (and (not A) (not B) N)) (not B)))
      (a!47 (and A (not B) (not G) H (not I) (not (and (not N) (not B)))))
      (a!60 (and (not (and D1 N1 (not P))) (not (and P Z))))
      (a!61 (and (not (and D1 O1 (not P))) (not (and P A1))))
      (a!62 (and (not (and D1 M1 (not P))) (not (and P Y))))
      (a!65 (and (not (and (not G) (not H) I)) C (not (and G (not H) (not I)))))
      (a!71 (and (not (and (not C) (not D) (not N))) (not C)))
      (a!72 (not (and C (not D) (not G) H (not I))))
      (a!78 (not (and C (not D) (not G) (not H) I)))
      (a!84 (not (and C (not D) G (not H) (not I))))
      (a!89 (and (not (and (not G) (not H) I)) D (not (and G (not H) (not I)))))
      (a!95 (and (not (and (not C) (not D) N)) (not D)))
      (a!96 (and C (not D) (not G) H (not I) (not (and (not N) (not D)))))
      (a!109 (not (and (not (and D1 F1)) (not P))))
      (a!111 (not (= (and (not P) (not D1)) F2)))
      (a!112 (and (not (and (not B1) W)) (not Q)))
      (a!114 (and (not (and (not C1) (not P))) (not (and (not R) P)) (not B1) W))
      (a!115 (and (not (and (not Q) P)) (not B1) W))
      (a!116 (and (not (and (not B1) W)) (not S)))
      (a!117 (and (not (and (not G) (not H) (not I))) W))
      (a!124 (and (not (and (not T) (not U))) (not V)))
      (a!129 (and (not B1) W (not (and P (not X)))))
      (a!130 (and (not A) B Q (not (and (not C1) (not X)))))
      (a!131 (and (not A)
                  (not B)
                  S
                  (not (and (not C1) (not X)))
                  (not (and (not A) B S))))
      (a!132 (and A (not B) S (not (and (not C1) (not X)))))
      (a!135 (and (not (and A (not B) S))
                  (not A)
                  B
                  Q
                  (not (and (not C1) (not X)))))
      (a!137 (and (not A) B S (not (and (not C1) (not X)))))
      (a!139 (and A (not B) G (not H) (not I) (not (and C (not D)))))
      (a!141 (and (not (and (not A) (not B))) G (not H) (not I)))
      (a!144 (and (not (and A (not B) (not N))) (not B)))
      (a!145 (and (not (and (not A) (not B))) (not (and (not G) H (not I)))))
      (a!151 (and (not (and O (not J))) (not B1)))
      (a!153 (and (not (and G (not H) (not I))) (not (and (not G) (not H) I))))
      (a!156 (and (not G) H (not I) N (not (and (not G) H I))))
      (a!161 (and (not (and K1 (not P1))) (not E1)))
      (a!163 (and (not (and D1 (not F1)))
                  (not (and (not D1) (not Q1)))
                  K1
                  (not P1)))
      (a!164 (and (not (and D1 (not E1))) K1 (not P1)))
      (a!165 (and (not (and K1 (not P1))) (not G1)))
      (a!166 (and (not (and (not G) (not H) (not I))) K1))
      (a!173 (and (not (and (not H1) (not I1))) (not J1)))
      (a!178 (and (not (and (not L1) D1)) K1 (not P1)))
      (a!179 (and (not C) D E1 (not (and (not L1) (not Q1)))))
      (a!180 (and (not C)
                  (not D)
                  G1
                  (not (and (not L1) (not Q1)))
                  (not (and (not C) D G1))))
      (a!181 (and C (not D) G1 (not (and (not L1) (not Q1)))))
      (a!184 (and (not (and C (not D) G1))
                  (not C)
                  D
                  E1
                  (not (and (not L1) (not Q1)))))
      (a!186 (and (not C) D G1 (not (and (not L1) (not Q1)))))
      (a!188 (and C (not D) G (not H) (not I) (not (and A (not B)))))
      (a!190 (and (not (and (not C) (not D))) G (not H) (not I)))
      (a!193 (and (not (and C (not D) (not N))) (not D)))
      (a!194 (and (not (and (not C) (not D))) (not (and (not G) H (not I)))))
      (a!200 (and (not (and O (not M))) (not P1))))
(let ((a!2 (and (not a!1) (not (and E (not F) (not G) H))))
      (a!4 (and (not a!3) (not (and (not E) F)) J))
      (a!5 (and (not a!3) (not (and (not E) F))))
      (a!7 (and (not a!6) (not (and (not G) H K (not L)))))
      (a!23 (and (not (and (not a!21) a!22))
                 (not (and (not N) A (not B) (not G) H (not I)))))
      (a!25 (and (not a!21) (not (and A (not B)))))
      (a!29 (and a!28 A (not (and G (not H) (not I)))))
      (a!36 (not (and (not (and a!34 E)) a!35)))
      (a!48 (and (not (and a!22 (not a!46))) (not a!47)))
      (a!50 (and (not a!46) (not (and A (not B)))))
      (a!53 (and (not (and a!28 (not B))) (not (and G (not H) (not I)))))
      (a!73 (and (not (and (not a!71) a!72))
                 (not (and (not N) C (not D) (not G) H (not I)))))
      (a!75 (and (not a!71) (not (and C (not D)))))
      (a!79 (and a!78 C (not (and G (not H) (not I)))))
      (a!85 (not (and (not (and a!84 K)) a!35)))
      (a!97 (and (not (and a!72 (not a!95))) (not a!96)))
      (a!99 (and (not a!95) (not (and C (not D)))))
      (a!102 (and (not (and a!78 (not D))) (not (and G (not H) (not I)))))
      (a!110 (and (not (and (not R) P)) a!109))
      (a!113 (and (not (and (not Q) P (not B1) W)) (not a!112)))
      (a!133 (and (not (and (not a!130) (not a!131))) (not a!132)))
      (a!136 (and (not (and (not a!135) (not a!132)))
                  (not (and A (not B) Q C1))))
      (a!138 (and (not (and A (not B) Q C1))
                  (not a!132)
                  (not a!130)
                  (not (and (not a!131) (not a!137)))))
      (a!142 (and a!28 (not (and G (not H) (not I)))))
      (a!146 (and (not (and (not a!144) (not G) H (not I))) (not a!145)))
      (a!157 (and (not (and (not G) H I N)) (not a!156)))
      (a!162 (and (not (and D1 (not E1) K1 (not P1))) (not a!161)))
      (a!182 (and (not (and (not a!179) (not a!180))) (not a!181)))
      (a!185 (and (not (and (not a!184) (not a!181)))
                  (not (and C (not D) E1 Q1))))
      (a!187 (and (not (and C (not D) E1 Q1))
                  (not a!181)
                  (not a!179)
                  (not (and (not a!180) (not a!186)))))
      (a!191 (and a!78 (not (and G (not H) (not I)))))
      (a!195 (and (not (and (not a!193) (not G) H (not I))) (not a!194))))
(let ((a!8 (and (not a!4) (not (and (not a!5) M)) (not a!7)))
      (a!24 (and (not a!23) (not (and (not G) H I))))
      (a!26 (and (not a!25) (not (and (not N) A (not B)))))
      (a!30 (and (not a!29) (not (and (not a!21) G (not H) (not I)))))
      (a!33 (and (not (and E (not F)))
                 (not (and (not G) (not H) I))
                 (not (and (not a!2) (not J)))))
      (a!37 (and a!36
                 (not (and E (not F)))
                 (not (and (not G) (not H) I))
                 (not (and (not a!2) (not J)))))
      (a!49 (and (not a!48) (not (and (not G) H I))))
      (a!51 (and (not a!50) (not (and A (not B) N))))
      (a!54 (and (not a!53) (not (and (not a!46) G (not H) (not I)))))
      (a!57 (and a!34
                 F
                 (not (and E (not F)))
                 (not (and (not G) (not H) I))
                 (not (and (not a!2) (not J)))))
      (a!74 (and (not a!73) (not (and (not G) H I))))
      (a!76 (and (not a!75) (not (and (not N) C (not D)))))
      (a!80 (and (not a!79) (not (and (not a!71) G (not H) (not I)))))
      (a!98 (and (not a!97) (not (and (not G) H I))))
      (a!100 (and (not a!99) (not (and C (not D) N))))
      (a!103 (and (not a!102) (not (and (not a!95) G (not H) (not I)))))
      (a!118 (and A
                  (not B)
                  (not (and E (not F)))
                  (not (and (not G) (not H) I))
                  (not (and (not a!2) (not J)))
                  O
                  G
                  (not H)
                  (not I)))
      (a!134 (and (not a!133) (not (and A (not B) Q C1))))
      (a!140 (and (not a!139)
                  (not (and E (not F)))
                  (not (and (not G) (not H) I))
                  (not (and (not a!2) (not J)))))
      (a!143 (and (not (and (not a!141) (not a!142)))
                  (not (and G (not H) I))
                  (not (and (not G) H))))
      (a!147 (and (not a!146) (not (and (not G) H I))))
      (a!183 (and (not a!182) (not (and C (not D) E1 Q1))))
      (a!192 (and (not (and (not a!190) (not a!191)))
                  (not (and G (not H) I))
                  (not (and (not G) H))))
      (a!196 (and (not a!195) (not (and (not G) H I)))))
(let ((a!9 (and (not (and E (not F)))
                (not (and (not G) (not H) I))
                (not (and (not a!2) (not J)))
                (not (and K (not L)))
                (not a!8)))
      (a!15 (and (not (and E (not F)))
                 (not (and (not G) (not H) I))
                 (not (and (not a!2) (not J)))
                 (not (and K (not L)))
                 (not a!8)
                 (not N)))
      (a!27 (and (not a!24) (not (and (not a!26) (not G) H I))))
      (a!31 (and (not a!30) (not (and G (not H) I)) (not (and (not G) H))))
      (a!52 (and (not a!49) (not (and (not a!51) (not G) H I))))
      (a!55 (and (not a!54) (not (and G (not H) I)) (not (and (not G) H))))
      (a!77 (and (not a!74) (not (and (not a!76) (not G) H I))))
      (a!81 (and (not a!80) (not (and G (not H) I)) (not (and (not G) H))))
      (a!83 (and (not (and (not G) (not H) I)) (not (and K (not L))) (not a!8)))
      (a!86 (and a!85
                 (not (and (not G) (not H) I))
                 (not (and K (not L)))
                 (not a!8)))
      (a!101 (and (not a!98) (not (and (not a!100) (not G) H I))))
      (a!104 (and (not a!103) (not (and G (not H) I)) (not (and (not G) H))))
      (a!106 (and a!84
                  L
                  (not (and (not G) (not H) I))
                  (not (and K (not L)))
                  (not a!8)))
      (a!119 (and (not a!117) (not P) (not a!118) (not (and (not a!33) O))))
      (a!120 (and (not (and (not U) (not V)))
                  (not T)
                  (not a!117)
                  (not P)
                  (not a!118)
                  (not (and (not a!33) O))))
      (a!122 (and (not (and (not T) U))
                  (not (and T (not U)))
                  (not (and (not U) (not V) (not T)))
                  (not a!117)
                  (not P)
                  (not a!118)
                  (not (and (not a!33) O))))
      (a!125 (and (not (and (not T) (not U) V))
                  (not a!124)
                  (not (and (not U) (not V) (not T)))
                  (not a!117)
                  (not P)
                  (not a!118)
                  (not (and (not a!33) O))))
      (a!127 (and (not (and (not U) (not V) (not T)))
                  (not a!117)
                  (not P)
                  (not a!118)
                  (not (and (not a!33) O))))
      (a!148 (and (not (and (not a!144) (not G) H I)) (not a!147)))
      (a!167 (and C
                  (not D)
                  (not (and (not G) (not H) I))
                  (not (and K (not L)))
                  (not a!8)
                  O
                  G
                  (not H)
                  (not I)))
      (a!189 (and (not a!188)
                  (not (and (not G) (not H) I))
                  (not (and K (not L)))
                  (not a!8)))
      (a!197 (and (not (and (not a!193) (not G) H I)) (not a!196))))
(let ((a!10 (and (not (and N A)) (not (and (not a!9) (not N)))))
      (a!11 (and (not a!9) (not N) (not (and (not G) H))))
      (a!16 (and (not a!14) (not (and (not a!15) A G (not H) (not I)))))
      (a!32 (and (not (and (not a!27) (not a!13))) (not a!31)))
      (a!41 (and (not a!40) (not (and (not a!15) B G (not H) (not I)))))
      (a!56 (and (not (and (not a!52) (not a!13))) (not a!55)))
      (a!63 (and (not (and N C)) (not (and (not a!9) (not N)))))
      (a!66 (and (not a!65) (not (and (not a!15) C G (not H) (not I)))))
      (a!82 (and (not (and (not a!77) (not a!13))) (not a!81)))
      (a!90 (and (not a!89) (not (and (not a!15) D G (not H) (not I)))))
      (a!105 (and (not (and (not a!101) (not a!13))) (not a!104)))
      (a!121 (and (not (and (not a!119) T)) (not a!120)))
      (a!123 (and (not (and (not a!119) U)) (not a!122)))
      (a!126 (and (not (and (not a!119) V)) (not a!125)))
      (a!128 (and (not a!127) (not (and (not a!119) (not W)))))
      (a!149 (and (not a!143) (not (and (not a!148) (not a!13)))))
      (a!154 (and (not (and (not a!15) G (not H) (not I))) (not a!153)))
      (a!168 (and (not a!166) (not D1) (not a!167) (not (and (not a!83) O))))
      (a!169 (and (not (and (not I1) (not J1)))
                  (not H1)
                  (not a!166)
                  (not D1)
                  (not a!167)
                  (not (and (not a!83) O))))
      (a!171 (and (not (and (not H1) I1))
                  (not (and H1 (not I1)))
                  (not (and (not I1) (not J1) (not H1)))
                  (not a!166)
                  (not D1)
                  (not a!167)
                  (not (and (not a!83) O))))
      (a!174 (and (not a!166)
                  (not D1)
                  (not a!167)
                  (not (and (not a!83) O))
                  (not (and (not I1) (not J1) (not H1)))
                  (not (and (not H1) (not I1) J1))
                  (not a!173)))
      (a!176 (and (not a!166)
                  (not D1)
                  (not a!167)
                  (not (and (not a!83) O))
                  (not (and (not I1) (not J1) (not H1)))))
      (a!198 (and (not a!192) (not (and (not a!197) (not a!13))))))
(let ((a!12 (and (not (and (not a!10) (not G) H)) (not a!11)))
      (a!17 (and (not a!16) (not (and G (not H) I)) (not (and (not G) H))))
      (a!38 (and (not (and (not a!32) (not a!33))) (not a!37)))
      (a!42 (and (not a!41) (not (and G (not H) I)) (not (and (not G) H))))
      (a!58 (and (not (and (not a!56) (not a!33))) (not a!57)))
      (a!64 (and (not (and (not a!63) (not G) H)) (not a!11)))
      (a!67 (and (not a!66) (not (and G (not H) I)) (not (and (not G) H))))
      (a!87 (and (not (and (not a!82) (not a!83))) (not a!86)))
      (a!91 (and (not a!90) (not (and G (not H) I)) (not (and (not G) H))))
      (a!107 (and (not (and (not a!105) (not a!83))) (not a!106)))
      (a!150 (and (not a!140) (not (and (not a!149) (not a!33)))))
      (a!155 (and (not a!154) (not (and G (not H) I)) (not (and (not G) H))))
      (a!170 (and (not (and (not a!168) H1)) (not a!169)))
      (a!172 (and (not (and (not a!168) I1)) (not a!171)))
      (a!175 (and (not (and (not a!168) J1)) (not a!174)))
      (a!177 (and (not a!176) (not (and (not a!168) (not K1)))))
      (a!199 (and (not a!189) (not (and (not a!198) (not a!83))))))
(let ((a!18 (and (not (and (not a!12) (not a!13))) (not a!17)))
      (a!43 (and (not a!42) (not (and N B (not G) H))))
      (a!68 (and (not (and (not a!64) (not a!13))) (not a!67)))
      (a!92 (and (not a!91) (not (and N D (not G) H))))
      (a!152 (and (not (and (not a!150) O (not J))) (not a!151)))
      (a!158 (and (not a!155) (not (and (not a!13) (not a!157))) J))
      (a!201 (and (not (and (not a!199) O (not M))) (not a!200)))
      (a!202 (and (not a!155) (not (and (not a!13) (not a!157))) M)))
(let ((a!19 (and (not (and (not J) A)) (not (and (not a!18) J))))
      (a!44 (and (not (and (not J) B)) (not (and (not a!43) J))))
      (a!69 (and (not (and (not M) C)) (not (and (not a!68) M))))
      (a!93 (and (not (and (not M) D)) (not (and (not a!92) M))))
      (a!159 (and (not a!158) (not (and O (not J)))))
      (a!203 (and (not (and O (not M))) (not a!202))))
(let ((a!20 (and (not a!19) (not (and O (not J)))))
      (a!45 (and (not a!44) (not (and O (not J)))))
      (a!70 (and (not a!69) (not (and O (not M)))))
      (a!94 (and (not a!93) (not (and O (not M)))))
      (a!160 (and (not (and (not a!152) O (not J))) (not a!159)))
      (a!204 (and (not (and (not a!201) O (not M))) (not a!203))))
(let ((a!39 (and (not a!20) (not (and (not a!38) O (not J)))))
      (a!59 (and (not a!45) (not (and O (not J) (not a!58)))))
      (a!88 (and (not a!70) (not (and (not a!87) O (not M)))))
      (a!108 (and (not a!94) (not (and (not a!107) O (not M))))))
(let ((a!205 (and (Invariant A
                       B
                       C
                       D
                       E
                       F
                       G
                       H
                       I
                       J
                       K
                       L
                       M
                       N
                       O
                       P
                       Q
                       R
                       S
                       T
                       U
                       V
                       W
                       X
                       Y
                       Z
                       A1
                       B1
                       C1
                       D1
                       E1
                       F1
                       G1
                       H1
                       I1
                       J1
                       K1
                       L1
                       M1
                       N1
                       O1
                       P1
                       Q1)
                  (= R1 E)
                  (= S1 F)
                  (= T1 K)
                  (= U1 L)
                  (not (= a!39 V1))
                  (not (= a!59 W1))
                  (not (= a!60 X1))
                  (not (= a!61 Y1))
                  (not (= a!62 Z1))
                  (= A2 P)
                  (not (= a!88 B2))
                  (not (= a!108 C2))
                  (= D2 (and (not P) D1))
                  (= E2 a!110)
                  a!111
                  (= G2 (and (not B1) P))
                  (= H2 a!113)
                  (= I2 a!114)
                  (= J2 (and (not a!115) (not a!116)))
                  (not (= a!121 K2))
                  (not (= a!123 L2))
                  (not (= a!126 M2))
                  (= N2 a!128)
                  (= O2 a!129)
                  (not (= a!134 P2))
                  (= Q2 a!136)
                  (= R2 a!138)
                  (= S2 a!160)
                  (= T2 (and C1 P (not B1) W))
                  (= U2 (and D1 (not P1)))
                  (= V2 a!162)
                  (= W2 a!163)
                  (= X2 (and (not a!164) (not a!165)))
                  (not (= a!170 Y2))
                  (not (= a!172 Z2))
                  (not (= a!175 A3))
                  (= B3 a!177)
                  (= C3 a!178)
                  (not (= a!183 D3))
                  (= E3 a!185)
                  (= F3 a!187)
                  (= G3 a!204)
                  (= H3 (and K1 (not P1) D1 Q1)))))
  (=> a!205
      (Invariant R1
           S1
           T1
           U1
           V1
           W1
           X1
           Y1
           Z1
           A2
           B2
           C2
           D2
           E2
           F2
           G2
           H2
           I2
           J2
           K2
           L2
           M2
           N2
           O2
           P2
           Q2
           R2
           S2
           T2
           U2
           V2
           W2
           X2
           Y2
           Z2
           A3
           B3
           C3
           D3
           E3
           F3
           G3
           H3))))))))))))))
(rule (let ((a!1 (and (not (and O3 (not N3))) M3 (not L3)))
      (a!2 (and O3 (not N3) (not (and M3 (not L3)))))
      (a!3 (and (not K3) (not J3) (not (and (not I3) (not H3)))))
      (a!6 (and (not (and I3 (not H3) (not G3)))
                (not (and (not I3) H3 (not G3)))
                (not (and (not I3) H3 G3))
                (not (and K3 (not J3) (not I3) (not H3) G3))
                (not (and (not K3) (not J3) I3 (not H3) G3))))
      (a!9 (and (not (and (not I3) (not H3))) (not E3) (not D3))))
(let ((a!4 (and (not a!3) (not (and K3 (not J3) (not I3) H3))))
      (a!7 (and (not a!6) (not (and (not K3) J3)) F3))
      (a!8 (and (not a!6) (not (and (not K3) J3))))
      (a!10 (and (not a!9) (not (and (not I3) H3 E3 (not D3))))))
(let ((a!5 (and (not (and K3 (not J3)))
                (not (and (not I3) (not H3) G3))
                (not (and (not a!4) (not F3)))))
      (a!11 (and (not a!7) (not (and (not a!8) C3)) (not a!10))))
(let ((a!12 (and O3
                 (not N3)
                 (not a!5)
                 M3
                 (not L3)
                 (not (and (not I3) (not H3) G3))
                 (not (and E3 (not D3)))
                 (not a!11))))
(let ((a!13 (and (Invariant O3
                      N3
                      M3
                      L3
                      K3
                      J3
                      I3
                      H3
                      G3
                      F3
                      E3
                      D3
                      C3
                      B3
                      A3
                      Z2
                      Y2
                      X2
                      W2
                      V2
                      U2
                      T2
                      S2
                      R2
                      Q2
                      P2
                      O2
                      N2
                      M2
                      L2
                      K2
                      J2
                      I2
                      H2
                      G2
                      F2
                      E2
                      D2
                      C2
                      B2
                      A2
                      Z1
                      Y1)
                 (not (and (not a!1) (not a!2) (not a!12))))))
  (=> a!13 Goal)))))))
(query Goal)
