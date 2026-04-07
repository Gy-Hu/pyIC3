(set-option :fp.engine spacer)
(set-logic ALL)
(declare-rel Invariant (Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool))
(declare-rel Goal ())
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
(declare-var P3 Bool)
(declare-var Q3 Bool)
(declare-var R3 Bool)
(declare-var S3 Bool)
(declare-var T3 Bool)
(declare-var U3 Bool)
(declare-var V3 Bool)
(declare-var W3 Bool)
(declare-var X3 Bool)
(declare-var Y3 Bool)
(declare-var Z3 Bool)
(declare-var A4 Bool)
(declare-var B4 Bool)
(declare-var C4 Bool)
(declare-var D4 Bool)
(declare-var E4 Bool)
(declare-var F4 Bool)
(declare-var G4 Bool)
(declare-var H4 Bool)
(declare-var I4 Bool)
(declare-var J4 Bool)
(declare-var K4 Bool)
(declare-var L4 Bool)
(declare-var M4 Bool)
(declare-var N4 Bool)
(declare-var O4 Bool)
(declare-var P4 Bool)
(declare-var Q4 Bool)
(declare-var R4 Bool)
(declare-var S4 Bool)
(declare-var T4 Bool)
(declare-var U4 Bool)
(declare-var V4 Bool)
(declare-var W4 Bool)
(declare-var X4 Bool)
(declare-var Y4 Bool)
(declare-var Z4 Bool)
(declare-var A5 Bool)
(declare-var B5 Bool)
(declare-var C5 Bool)
(declare-var D5 Bool)
(rule (=> (and (not A)
         B
         (not C)
         D
         (not E)
         F
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
         R
         (not S)
         (not T)
         U
         (not V)
         W
         X
         Y
         (not Z)
         A1
         (not B1)
         (not C1)
         (not D1)
         (not E1)
         (not F1)
         (not G1)
         H1
         (not I1)
         (not J1)
         K1
         (not L1)
         M1
         N1
         O1
         (not P1)
         Q1
         (not R1)
         (not S1)
         (not T1)
         (not U1)
         (not V1)
         (not W1)
         X1
         (not Y1)
         (not Z1)
         A2
         (not B2)
         C2
         D2
         E2
         (not F2)
         G2
         (not H2)
         (not I2)
         (not J2))
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
         Q1
         R1
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
         J2)))
(rule (let ((a!1 (not (and (not (and U1 W1)) (not E1))))
      (a!4 (not (= (and (not E1) (not U1) (not O)) U2)))
      (a!5 (and (not (and F2 U1 (not E1))) (not (and E1 P1))))
      (a!7 (and (not (and G2 U1 (not E1))) (not (and E1 Q1))))
      (a!9 (and (not (and H2 U1 (not E1))) (not (and E1 R1))))
      (a!11 (and (not (and X (not C1))) (not P)))
      (a!13 (and (not (and (not D1) (not O))) (not (and (not Q) O)) X (not C1)))
      (a!14 (and (not (and (not P) O)) X (not C1)))
      (a!15 (and (not (and X (not C1))) (not R)))
      (a!16 (and (not (and M (not N) (not L)))
                 (not (and (not M) N (not L)))
                 (not (and (not M) N L))
                 (not (and S (not T) (not M) (not N) L))
                 (not (and (not S) (not T) M (not N) L))))
      (a!21 (and (not (and I1 (not J1) (not M) (not N) L))
                 (not (and M (not N) (not L)))
                 (not (and (not M) N (not L)))
                 (not (and (not M) N L))
                 (not (and (not I1) (not J1) M (not N) L))))
      (a!25 (and (not Y1) (not Z1) (not (and (not M) (not N)))))
      (a!28 (and (not S) (not T) (not (and (not M) (not N)))))
      (a!30 (and (not I1) (not J1) (not (and (not M) (not N)))))
      (a!37 (and (not (and M (not N) L)) (not (and (not M) N))))
      (a!38 (and (not (and (not M) (not N) L)) A (not (and M (not N) (not L)))))
      (a!45 (and (not (and (not A) (not B) (not J))) (not A)))
      (a!46 (not (and A (not B) (not M) N (not L))))
      (a!52 (not (and A (not B) (not M) (not N) L)))
      (a!58 (not (and A (not B) M (not N) (not L))))
      (a!59 (not (and A (not B) C (not D) E (not F) M (not N) (not L))))
      (a!64 (and (not (and (not M) (not N) L)) B (not (and M (not N) (not L)))))
      (a!70 (and (not (and (not A) (not B) J)) (not B)))
      (a!71 (and A (not B) (not M) N (not L) (not (and (not B) (not J)))))
      (a!84 (and (not (and (not M) (not N) (not L))) X))
      (a!91 (and (not (and (not U) (not V))) (not W)))
      (a!96 (and (not (and (not Y) O)) X (not C1)))
      (a!97 (and (not A) B P (not (and (not Y) (not D1)))))
      (a!98 (and (not A)
                 (not B)
                 R
                 (not (and (not Y) (not D1)))
                 (not (and (not A) B R))))
      (a!99 (and A (not B) R (not (and (not Y) (not D1)))))
      (a!102 (and (not (and A (not B) R))
                  (not A)
                  B
                  P
                  (not (and (not Y) (not D1)))))
      (a!104 (and (not A) B R (not (and (not Y) (not D1)))))
      (a!106 (not (and A (not B) C (not D) E (not F))))
      (a!108 (and (not (and (not A) (not B))) M (not N) (not L)))
      (a!111 (and (not (and A (not B) (not J))) (not B)))
      (a!112 (and (not (and (not A) (not B))) (not (and (not M) N (not L)))))
      (a!118 (and (not (and K (not G))) (not C1)))
      (a!120 (and (not (and M (not N) (not L))) (not (and (not M) (not N) L))))
      (a!123 (and (not (and (not M) N L)) (not M) N (not L) J))
      (a!128 (and (not (and N1 (not S1))) (not F1)))
      (a!130 (and (not (and (not E1) (not T1)))
                  (not (and E1 (not G1)))
                  N1
                  (not S1)))
      (a!131 (and (not (and E1 (not F1))) N1 (not S1)))
      (a!132 (and (not (and N1 (not S1))) (not H1)))
      (a!135 (and (not (and (not M) (not N) L)) C (not (and M (not N) (not L)))))
      (a!141 (and (not (and (not C) (not D) (not J))) (not C)))
      (a!142 (not (and C (not D) (not M) N (not L))))
      (a!148 (not (and C (not D) (not M) (not N) L)))
      (a!154 (not (and C (not D) M (not N) (not L))))
      (a!159 (and (not (and (not M) (not N) L)) D (not (and M (not N) (not L)))))
      (a!165 (and (not (and (not C) (not D) J)) (not D)))
      (a!166 (and C (not D) (not M) N (not L) (not (and (not J) (not D)))))
      (a!179 (and (not (and (not M) (not N) (not L))) N1))
      (a!186 (and (not (and (not K1) (not L1))) (not M1)))
      (a!191 (and (not (and E1 (not O1))) N1 (not S1)))
      (a!192 (and (not C) D F1 (not (and (not O1) (not T1)))))
      (a!193 (and (not C)
                  (not D)
                  H1
                  (not (and (not O1) (not T1)))
                  (not (and (not C) D H1))))
      (a!194 (and C (not D) H1 (not (and (not O1) (not T1)))))
      (a!197 (and (not (and C (not D) H1))
                  (not C)
                  D
                  F1
                  (not (and (not O1) (not T1)))))
      (a!199 (and (not C) D H1 (not (and (not O1) (not T1)))))
      (a!202 (and (not (and (not C) (not D))) M (not N) (not L)))
      (a!205 (and (not (and C (not D) (not J))) (not D)))
      (a!206 (and (not (and (not C) (not D))) (not (and (not M) N (not L)))))
      (a!212 (and (not (and K (not H))) (not S1)))
      (a!217 (and (not (and D2 (not I2))) (not V1)))
      (a!219 (and (not (and U1 (not W1)))
                  (not (and (not U1) (not J2)))
                  D2
                  (not I2)))
      (a!220 (and (not (and (not V1) U1)) D2 (not I2)))
      (a!221 (and (not (and D2 (not I2))) (not X1)))
      (a!224 (and (not (and (not M) (not N) L)) E (not (and M (not N) (not L)))))
      (a!230 (and (not (and (not E) (not F) (not J))) (not E)))
      (a!231 (not (and E (not F) (not M) N (not L))))
      (a!237 (not (and E (not F) (not M) (not N) L)))
      (a!243 (not (and E (not F) M (not N) (not L))))
      (a!248 (and (not (and (not M) (not N) L)) F (not (and M (not N) (not L)))))
      (a!254 (and (not (and (not E) (not F) J)) (not F)))
      (a!255 (and E (not F) (not M) N (not L) (not (and (not F) (not J)))))
      (a!268 (and (not (and (not M) (not N) (not L))) D2))
      (a!275 (and (not (and (not A2) (not B2))) (not C2)))
      (a!280 (and (not (and U1 (not E2))) D2 (not I2)))
      (a!281 (and (not E) F V1 (not (and (not E2) (not J2)))))
      (a!282 (and (not E)
                  (not F)
                  X1
                  (not (and (not E2) (not J2)))
                  (not (and (not E) F X1))))
      (a!283 (and E (not F) X1 (not (and (not E2) (not J2)))))
      (a!286 (and (not (and E (not F) X1))
                  (not E)
                  F
                  V1
                  (not (and (not E2) (not J2)))))
      (a!288 (and (not E) F X1 (not (and (not E2) (not J2)))))
      (a!290 (and (not (and A (not B) C (not D))) E (not F) M (not N) (not L)))
      (a!292 (and (not (and (not E) (not F))) M (not N) (not L)))
      (a!295 (and (not (and E (not F) (not J))) (not F)))
      (a!296 (and (not (and (not E) (not F))) (not (and (not M) N (not L)))))
      (a!302 (and (not (and K (not I))) (not I2))))
(let ((a!2 (and (not (and E1 (not G1))) a!1))
      (a!6 (and (not (and (not a!5) (not O))) (not (and Z O))))
      (a!8 (and (not (and (not a!7) (not O))) (not (and A1 O))))
      (a!10 (and (not (and (not a!9) (not O))) (not (and B1 O))))
      (a!12 (and (not (and (not P) O X (not C1))) (not a!11)))
      (a!17 (and (not a!16) (not (and (not S) T)) G))
      (a!18 (and (not a!16) (not (and (not S) T))))
      (a!26 (and (not a!25) (not (and Y1 (not Z1) (not M) N))))
      (a!29 (and (not a!28) (not (and S (not T) (not M) N))))
      (a!31 (and (not a!30) (not (and I1 (not J1) (not M) N))))
      (a!47 (and (not (and (not a!45) a!46))
                 (not (and A (not J) (not B) (not M) N (not L)))))
      (a!49 (and (not a!45) (not (and A (not B)))))
      (a!53 (and a!52 A (not (and M (not N) (not L)))))
      (a!60 (not (and (not (and a!58 S)) a!59)))
      (a!72 (and (not (and a!46 (not a!70))) (not a!71)))
      (a!74 (and (not a!70) (not (and A (not B)))))
      (a!77 (and (not (and a!52 (not B))) (not (and M (not N) (not L)))))
      (a!100 (and (not (and (not a!97) (not a!98))) (not a!99)))
      (a!103 (and (not (and (not a!102) (not a!99))) (not (and A (not B) P D1))))
      (a!105 (and (not (and A (not B) P D1))
                  (not a!99)
                  (not a!97)
                  (not (and (not a!98) (not a!104)))))
      (a!109 (and a!52 (not (and M (not N) (not L)))))
      (a!113 (and (not (and (not a!111) (not M) N (not L))) (not a!112)))
      (a!124 (and (not (and (not M) N L J)) (not a!123)))
      (a!129 (and (not (and E1 (not F1) N1 (not S1))) (not a!128)))
      (a!143 (and (not (and (not a!141) a!142))
                  (not (and (not J) C (not D) (not M) N (not L)))))
      (a!145 (and (not a!141) (not (and C (not D)))))
      (a!149 (and a!148 C (not (and M (not N) (not L)))))
      (a!155 (not (and (not (and a!154 I1)) a!59)))
      (a!167 (and (not (and a!142 (not a!165))) (not a!166)))
      (a!169 (and (not a!165) (not (and C (not D)))))
      (a!172 (and (not (and a!148 (not D))) (not (and M (not N) (not L)))))
      (a!195 (and (not (and (not a!192) (not a!193))) (not a!194)))
      (a!198 (and (not (and (not a!197) (not a!194)))
                  (not (and C (not D) F1 T1))))
      (a!200 (and (not (and C (not D) F1 T1))
                  (not a!194)
                  (not a!192)
                  (not (and (not a!193) (not a!199)))))
      (a!203 (and a!148 (not (and M (not N) (not L)))))
      (a!207 (and (not (and (not a!205) (not M) N (not L))) (not a!206)))
      (a!218 (and (not (and (not V1) U1 D2 (not I2))) (not a!217)))
      (a!232 (and (not (and (not a!230) a!231))
                  (not (and E (not J) (not F) (not M) N (not L)))))
      (a!234 (and (not a!230) (not (and E (not F)))))
      (a!238 (and a!237 E (not (and M (not N) (not L)))))
      (a!244 (not (and (not (and a!243 Y1)) a!59)))
      (a!256 (and (not (and a!231 (not a!254))) (not a!255)))
      (a!258 (and (not a!254) (not (and E (not F)))))
      (a!261 (and (not (and a!237 (not F))) (not (and M (not N) (not L)))))
      (a!284 (and (not (and (not a!281) (not a!282))) (not a!283)))
      (a!287 (and (not (and (not a!286) (not a!283)))
                  (not (and E (not F) V1 J2))))
      (a!289 (and (not (and E (not F) V1 J2))
                  (not a!283)
                  (not a!281)
                  (not (and (not a!282) (not a!288)))))
      (a!293 (and a!237 (not (and M (not N) (not L)))))
      (a!297 (and (not (and (not a!295) (not M) N (not L))) (not a!296))))
(let ((a!3 (and (not (and (not Q) O)) (not (and (not a!2) (not O)))))
      (a!19 (and (not a!17) (not (and (not a!18) H))))
      (a!23 (and (not a!21) (not (and (not I1) J1)) (not a!18)))
      (a!32 (and (not a!17) (not (and (not a!18) H)) (not a!31)))
      (a!48 (and (not a!47) (not (and (not M) N L))))
      (a!50 (and (not a!49) (not (and A (not J) (not B)))))
      (a!54 (and (not a!53) (not (and (not a!45) M (not N) (not L)))))
      (a!57 (and (not (and S (not T)))
                 (not (and (not M) (not N) L))
                 (not (and (not a!29) (not G)))))
      (a!61 (and a!60
                 (not (and S (not T)))
                 (not (and (not M) (not N) L))
                 (not (and (not a!29) (not G)))))
      (a!73 (and (not a!72) (not (and (not M) N L))))
      (a!75 (and (not a!74) (not (and A (not B) J))))
      (a!78 (and (not a!77) (not (and (not a!70) M (not N) (not L)))))
      (a!81 (and a!58
                 T
                 (not (and S (not T)))
                 (not (and (not M) (not N) L))
                 (not (and (not a!29) (not G)))))
      (a!85 (and (not (and S (not T)))
                 (not (and (not M) (not N) L))
                 (not (and (not a!29) (not G)))
                 K
                 M
                 (not N)
                 (not L)
                 A
                 (not B)))
      (a!101 (and (not a!100) (not (and A (not B) P D1))))
      (a!107 (and (not (and A (not B) M (not N) (not L) a!106))
                  (not (and S (not T)))
                  (not (and (not M) (not N) L))
                  (not (and (not a!29) (not G)))))
      (a!110 (and (not (and (not a!108) (not a!109)))
                  (not (and M (not N) L))
                  (not (and (not M) N))))
      (a!114 (and (not a!113) (not (and (not M) N L))))
      (a!144 (and (not a!143) (not (and (not M) N L))))
      (a!146 (and (not a!145) (not (and (not J) C (not D)))))
      (a!150 (and (not a!149) (not (and (not a!141) M (not N) (not L)))))
      (a!168 (and (not a!167) (not (and (not M) N L))))
      (a!170 (and (not a!169) (not (and C (not D) J))))
      (a!173 (and (not a!172) (not (and (not a!165) M (not N) (not L)))))
      (a!196 (and (not a!195) (not (and C (not D) F1 T1))))
      (a!204 (and (not (and (not a!202) (not a!203)))
                  (not (and M (not N) L))
                  (not (and (not M) N))))
      (a!208 (and (not a!207) (not (and (not M) N L))))
      (a!233 (and (not a!232) (not (and (not M) N L))))
      (a!235 (and (not a!234) (not (and E (not J) (not F)))))
      (a!239 (and (not a!238) (not (and (not a!230) M (not N) (not L)))))
      (a!257 (and (not a!256) (not (and (not M) N L))))
      (a!259 (and (not a!258) (not (and E (not F) J))))
      (a!262 (and (not a!261) (not (and (not a!254) M (not N) (not L)))))
      (a!285 (and (not a!284) (not (and E (not F) V1 J2))))
      (a!294 (and (not (and (not a!292) (not a!293)))
                  (not (and M (not N) L))
                  (not (and (not M) N))))
      (a!298 (and (not a!297) (not (and (not M) N L)))))
(let ((a!20 (and (not a!19) (not a!16) (not (and (not S) T))))
      (a!22 (and (not a!21) (not (and (not I1) J1)) (not a!18) (not a!19)))
      (a!51 (and (not a!48) (not (and (not a!50) (not M) N L))))
      (a!55 (and (not a!54) (not (and M (not N) L)) (not (and (not M) N))))
      (a!76 (and (not a!73) (not (and (not a!75) (not M) N L))))
      (a!79 (and (not a!78) (not (and M (not N) L)) (not (and (not M) N))))
      (a!86 (and (not a!84) (not O) (not a!85) (not (and (not a!57) K))))
      (a!87 (and (not (and (not V) (not W)))
                 (not U)
                 (not a!84)
                 (not O)
                 (not a!85)
                 (not (and (not a!57) K))))
      (a!89 (and (not (and (not U) V))
                 (not (and U (not V)))
                 (not (and (not V) (not W) (not U)))
                 (not a!84)
                 (not O)
                 (not a!85)
                 (not (and (not a!57) K))))
      (a!92 (and (not a!84)
                 (not O)
                 (not a!85)
                 (not (and (not a!57) K))
                 (not (and (not V) (not W) (not U)))
                 (not (and (not U) (not V) W))
                 (not a!91)))
      (a!94 (and (not a!84)
                 (not O)
                 (not a!85)
                 (not (and (not a!57) K))
                 (not (and (not V) (not W) (not U)))))
      (a!115 (and (not (and (not a!111) (not M) N L)) (not a!114)))
      (a!147 (and (not a!144) (not (and (not a!146) (not M) N L))))
      (a!151 (and (not a!150) (not (and M (not N) L)) (not (and (not M) N))))
      (a!153 (and (not (and I1 (not J1)))
                  (not (and (not M) (not N) L))
                  (not a!32)))
      (a!156 (and a!155
                  (not (and I1 (not J1)))
                  (not (and (not M) (not N) L))
                  (not a!32)))
      (a!171 (and (not a!168) (not (and (not a!170) (not M) N L))))
      (a!174 (and (not a!173) (not (and M (not N) L)) (not (and (not M) N))))
      (a!176 (and a!154
                  J1
                  (not (and I1 (not J1)))
                  (not (and (not M) (not N) L))
                  (not a!32)))
      (a!180 (and (not (and I1 (not J1)))
                  (not (and (not M) (not N) L))
                  (not a!32)
                  K
                  M
                  (not N)
                  (not L)
                  C
                  (not D)))
      (a!201 (and (not (and a!106 C (not D) M (not N) (not L)))
                  (not (and I1 (not J1)))
                  (not (and (not M) (not N) L))
                  (not a!32)))
      (a!209 (and (not (and (not a!205) (not M) N L)) (not a!208)))
      (a!236 (and (not a!233) (not (and (not a!235) (not M) N L))))
      (a!240 (and (not a!239) (not (and M (not N) L)) (not (and (not M) N))))
      (a!260 (and (not a!257) (not (and (not a!259) (not M) N L))))
      (a!263 (and (not a!262) (not (and M (not N) L)) (not (and (not M) N))))
      (a!299 (and (not (and (not a!295) (not M) N L)) (not a!298))))
(let ((a!24 (and (not a!22) (not (and (not a!23) I))))
      (a!56 (and (not (and (not a!51) (not a!37))) (not a!55)))
      (a!80 (and (not (and (not a!76) (not a!37))) (not a!79)))
      (a!88 (and (not (and (not a!86) U)) (not a!87)))
      (a!90 (and (not (and (not a!86) V)) (not a!89)))
      (a!93 (and (not (and (not a!86) W)) (not a!92)))
      (a!95 (and (not a!94) (not (and (not a!86) (not X)))))
      (a!116 (and (not a!110) (not (and (not a!115) (not a!37)))))
      (a!152 (and (not (and (not a!147) (not a!37))) (not a!151)))
      (a!175 (and (not (and (not a!171) (not a!37))) (not a!174)))
      (a!181 (and (not a!179) (not E1) (not a!180) (not (and (not a!153) K))))
      (a!182 (and (not (and (not L1) (not M1)))
                  (not K1)
                  (not a!179)
                  (not E1)
                  (not a!180)
                  (not (and (not a!153) K))))
      (a!184 (and (not (and (not K1) L1))
                  (not (and K1 (not L1)))
                  (not (and (not L1) (not M1) (not K1)))
                  (not a!179)
                  (not E1)
                  (not a!180)
                  (not (and (not a!153) K))))
      (a!187 (and (not (and (not K1) (not L1) M1))
                  (not a!186)
                  (not (and (not L1) (not M1) (not K1)))
                  (not a!179)
                  (not E1)
                  (not a!180)
                  (not (and (not a!153) K))))
      (a!189 (and (not (and (not L1) (not M1) (not K1)))
                  (not a!179)
                  (not E1)
                  (not a!180)
                  (not (and (not a!153) K))))
      (a!210 (and (not a!204) (not (and (not a!209) (not a!37)))))
      (a!241 (and (not (and (not a!236) (not a!37))) (not a!240)))
      (a!264 (and (not (and (not a!260) (not a!37))) (not a!263)))
      (a!300 (and (not a!294) (not (and (not a!299) (not a!37))))))
(let ((a!27 (and (not a!20) (not (and (not a!24) (not a!18))) (not a!26)))
      (a!62 (and (not (and (not a!56) (not a!57))) (not a!61)))
      (a!82 (and (not (and (not a!80) (not a!57))) (not a!81)))
      (a!117 (and (not a!107) (not (and (not a!116) (not a!57)))))
      (a!157 (and (not (and (not a!152) (not a!153))) (not a!156)))
      (a!177 (and (not (and (not a!175) (not a!153))) (not a!176)))
      (a!183 (and (not (and (not a!181) K1)) (not a!182)))
      (a!185 (and (not (and (not a!181) L1)) (not a!184)))
      (a!188 (and (not (and (not a!181) M1)) (not a!187)))
      (a!190 (and (not a!189) (not (and (not a!181) (not N1)))))
      (a!211 (and (not a!201) (not (and (not a!210) (not a!153))))))
(let ((a!33 (and (not (and Y1 (not Z1)))
                 (not (and (not M) (not N) L))
                 (not a!27)
                 (not (and S (not T)))
                 (not (and (not a!29) (not G)))
                 (not (and I1 (not J1)))
                 (not a!32)))
      (a!39 (and (not (and Y1 (not Z1)))
                 (not (and (not M) (not N) L))
                 (not a!27)
                 (not (and S (not T)))
                 (not (and (not a!29) (not G)))
                 (not (and I1 (not J1)))
                 (not a!32)
                 (not J)))
      (a!119 (and (not (and (not a!117) K (not G))) (not a!118)))
      (a!213 (and (not (and (not a!211) K (not H))) (not a!212)))
      (a!242 (and (not (and Y1 (not Z1)))
                  (not (and (not M) (not N) L))
                  (not a!27)))
      (a!245 (and a!244
                  (not (and Y1 (not Z1)))
                  (not (and (not M) (not N) L))
                  (not a!27)))
      (a!265 (and a!243
                  Z1
                  (not (and Y1 (not Z1)))
                  (not (and (not M) (not N) L))
                  (not a!27)))
      (a!269 (and (not (and Y1 (not Z1)))
                  (not (and (not M) (not N) L))
                  (not a!27)
                  K
                  M
                  (not N)
                  (not L)
                  E
                  (not F)))
      (a!291 (and (not a!290)
                  (not (and Y1 (not Z1)))
                  (not (and (not M) (not N) L))
                  (not a!27))))
(let ((a!34 (and (not (and A J)) (not (and (not a!33) (not J)))))
      (a!35 (and (not a!33) (not J) (not (and (not M) N))))
      (a!40 (and (not a!38) (not (and (not a!39) A M (not N) (not L)))))
      (a!65 (and (not a!64) (not (and (not a!39) B M (not N) (not L)))))
      (a!121 (and (not (and (not a!39) M (not N) (not L))) (not a!120)))
      (a!133 (and (not (and J C)) (not (and (not a!33) (not J)))))
      (a!136 (and (not a!135) (not (and (not a!39) C M (not N) (not L)))))
      (a!160 (and (not a!159) (not (and (not a!39) D M (not N) (not L)))))
      (a!222 (and (not (and E J)) (not (and (not a!33) (not J)))))
      (a!225 (and (not a!224) (not (and (not a!39) E M (not N) (not L)))))
      (a!246 (and (not (and (not a!241) (not a!242))) (not a!245)))
      (a!249 (and (not a!248) (not (and (not a!39) F M (not N) (not L)))))
      (a!266 (and (not (and (not a!264) (not a!242))) (not a!265)))
      (a!270 (and (not a!268) (not U1) (not a!269) (not (and (not a!242) K))))
      (a!271 (and (not (and (not B2) (not C2)))
                  (not A2)
                  (not a!268)
                  (not U1)
                  (not a!269)
                  (not (and (not a!242) K))))
      (a!273 (and (not (and (not A2) B2))
                  (not (and A2 (not B2)))
                  (not (and (not B2) (not C2) (not A2)))
                  (not a!268)
                  (not U1)
                  (not a!269)
                  (not (and (not a!242) K))))
      (a!276 (and (not (and (not A2) (not B2) C2))
                  (not a!275)
                  (not (and (not B2) (not C2) (not A2)))
                  (not a!268)
                  (not U1)
                  (not a!269)
                  (not (and (not a!242) K))))
      (a!278 (and (not (and (not B2) (not C2) (not A2)))
                  (not a!268)
                  (not U1)
                  (not a!269)
                  (not (and (not a!242) K))))
      (a!301 (and (not a!291) (not (and (not a!300) (not a!242))))))
(let ((a!36 (and (not (and (not a!34) (not M) N)) (not a!35)))
      (a!41 (and (not a!40) (not (and M (not N) L)) (not (and (not M) N))))
      (a!66 (and (not a!65) (not (and M (not N) L)) (not (and (not M) N))))
      (a!122 (and (not a!121) (not (and M (not N) L)) (not (and (not M) N))))
      (a!134 (and (not (and (not a!133) (not M) N)) (not a!35)))
      (a!137 (and (not a!136) (not (and M (not N) L)) (not (and (not M) N))))
      (a!161 (and (not a!160) (not (and M (not N) L)) (not (and (not M) N))))
      (a!223 (and (not (and (not a!222) (not M) N)) (not a!35)))
      (a!226 (and (not a!225) (not (and M (not N) L)) (not (and (not M) N))))
      (a!250 (and (not a!249) (not (and M (not N) L)) (not (and (not M) N))))
      (a!272 (and (not (and (not a!270) A2)) (not a!271)))
      (a!274 (and (not (and (not a!270) B2)) (not a!273)))
      (a!277 (and (not (and (not a!270) C2)) (not a!276)))
      (a!279 (and (not a!278) (not (and (not a!270) (not D2)))))
      (a!303 (and (not (and (not a!301) K (not I))) (not a!302))))
(let ((a!42 (and (not (and (not a!36) (not a!37))) (not a!41)))
      (a!67 (and (not a!66) (not (and B J (not M) N))))
      (a!125 (and (not a!122) (not (and (not a!37) (not a!124))) G))
      (a!138 (and (not (and (not a!134) (not a!37))) (not a!137)))
      (a!162 (and (not a!161) (not (and J D (not M) N))))
      (a!214 (and (not a!122) (not (and (not a!37) (not a!124))) H))
      (a!227 (and (not (and (not a!223) (not a!37))) (not a!226)))
      (a!251 (and (not a!250) (not (and F J (not M) N))))
      (a!304 (and (not a!122) (not (and (not a!37) (not a!124))) I)))
(let ((a!43 (and (not (and A (not G))) (not (and (not a!42) G))))
      (a!68 (and (not (and B (not G))) (not (and (not a!67) G))))
      (a!126 (and (not (and K (not G))) (not a!125)))
      (a!139 (and (not (and (not H) C)) (not (and (not a!138) H))))
      (a!163 (and (not (and (not H) D)) (not (and (not a!162) H))))
      (a!215 (and (not (and K (not H))) (not a!214)))
      (a!228 (and (not (and E (not I))) (not (and (not a!227) I))))
      (a!252 (and (not (and F (not I))) (not (and (not a!251) I))))
      (a!305 (and (not (and K (not I))) (not a!304))))
(let ((a!44 (and (not a!43) (not (and K (not G)))))
      (a!69 (and (not a!68) (not (and K (not G)))))
      (a!127 (and (not (and (not a!119) K (not G))) (not a!126)))
      (a!140 (and (not a!139) (not (and K (not H)))))
      (a!164 (and (not a!163) (not (and K (not H)))))
      (a!216 (and (not (and (not a!213) K (not H))) (not a!215)))
      (a!229 (and (not a!228) (not (and K (not I)))))
      (a!253 (and (not a!252) (not (and K (not I)))))
      (a!306 (and (not (and (not a!303) K (not I))) (not a!305))))
(let ((a!63 (and (not a!44) (not (and (not a!62) K (not G)))))
      (a!83 (and (not a!69) (not (and (not a!82) K (not G)))))
      (a!158 (and (not a!140) (not (and (not a!157) K (not H)))))
      (a!178 (and (not a!164) (not (and (not a!177) K (not H)))))
      (a!247 (and (not a!229) (not (and (not a!246) K (not I)))))
      (a!267 (and (not a!253) (not (and (not a!266) K (not I))))))
(let ((a!307 (and (Invariant A
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
                       Q1
                       R1
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
                       J2)
                  (= K2 S)
                  (= L2 T)
                  (= M2 I1)
                  (= N2 J1)
                  (= O2 Y1)
                  (= P2 Z1)
                  (= Q2 O)
                  (= R2 (and E1 (not O)))
                  (= S2 (and (not E1) U1 (not O)))
                  (= T2 a!3)
                  a!4
                  (not (= a!6 V2))
                  (not (= a!8 W2))
                  (not (= a!10 X2))
                  (= Y2 (and (not C1) O))
                  (= Z2 a!12)
                  (= A3 a!13)
                  (= B3 (and (not a!14) (not a!15)))
                  (not (= a!63 C3))
                  (not (= a!83 D3))
                  (not (= a!88 E3))
                  (not (= a!90 F3))
                  (not (= a!93 G3))
                  (= H3 a!95)
                  (= I3 a!96)
                  (not (= a!101 J3))
                  (= K3 a!103)
                  (= L3 a!105)
                  (= M3 a!127)
                  (= N3 (and D1 O X (not C1)))
                  (= O3 (and E1 (not S1)))
                  (= P3 a!129)
                  (= Q3 a!130)
                  (= R3 (and (not a!131) (not a!132)))
                  (not (= a!158 S3))
                  (not (= a!178 T3))
                  (not (= a!183 U3))
                  (not (= a!185 V3))
                  (not (= a!188 W3))
                  (= X3 a!190)
                  (= Y3 a!191)
                  (not (= a!196 Z3))
                  (= A4 a!198)
                  (= B4 a!200)
                  (= C4 a!216)
                  (= D4 (and N1 (not S1) E1 T1))
                  (= E4 (and U1 (not I2)))
                  (= F4 a!218)
                  (= G4 a!219)
                  (= H4 (and (not a!220) (not a!221)))
                  (not (= a!247 I4))
                  (not (= a!267 J4))
                  (not (= a!272 K4))
                  (not (= a!274 L4))
                  (not (= a!277 M4))
                  (= N4 a!279)
                  (= O4 a!280)
                  (not (= a!285 P4))
                  (= Q4 a!287)
                  (= R4 a!289)
                  (= S4 a!306)
                  (= T4 (and D2 (not I2) U1 J2)))))
  (=> a!307
      (Invariant K2
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
           H3
           I3
           J3
           K3
           L3
           M3
           N3
           O3
           P3
           Q3
           R3
           S3
           T3
           U3
           V3
           W3
           X3
           Y3
           Z3
           A4
           B4
           C4
           D4
           E4
           F4
           G4
           H4
           I4
           J4
           K4
           L4
           M4
           N4
           O4
           P4
           Q4
           R4
           S4
           T4)))))))))))))))))
(rule (let ((a!1 (and D5 (not C5) (not (and B5 (not A5))) (not (and Z4 (not Y4)))))
      (a!2 (and B5 (not A5) (not (and Z4 (not Y4))) (not (and D5 (not C5)))))
      (a!3 (and (not (and D5 (not C5))) Z4 (not Y4) (not (and B5 (not A5))))))
(let ((a!4 (and (Invariant D5
                     C5
                     B5
                     A5
                     Z4
                     Y4
                     X4
                     W4
                     V4
                     U4
                     T4
                     S4
                     R4
                     Q4
                     P4
                     O4
                     N4
                     M4
                     L4
                     K4
                     J4
                     I4
                     H4
                     G4
                     F4
                     E4
                     D4
                     C4
                     B4
                     A4
                     Z3
                     Y3
                     X3
                     W3
                     V3
                     U3
                     T3
                     S3
                     R3
                     Q3
                     P3
                     O3
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
                     U2)
                (not (and (not a!1) (not a!2) (not a!3))))))
  (=> a!4 Goal))))
(query Goal)
