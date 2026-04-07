(set-option :fp.engine spacer)
(set-logic ALL)
(declare-rel Invariant (Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool))
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
(rule (=> (and (not A)
         (not B)
         (not C)
         (not D)
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
         (not S)
         (not T)
         (not U)
         (not V)
         (not W)
         (not X)
         (not Y)
         (not Z)
         (not A1)
         (not B1)
         (not C1)
         (not D1)
         (not E1)
         (not F1)
         (not G1)
         (not H1)
         (not I1)
         (not J1)
         (not K1))
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
         K1)))
(rule (let ((a!1 (and (not (and A B)) (not (and (not A) G3))))
      (a!2 (and (not (and A D)) (not (and (not A) H3))))
      (a!3 (and (not (and A F)) (not (and (not A) I3))))
      (a!4 (and (not (and (not E) (not C))) (not G)))
      (a!6 (and (not (and A H)) (not (and (not A) J3))))
      (a!7 (and (not (and E (not C))) (not I)))
      (a!9 (and (not (and A J)) (not (and (not A) K3))))
      (a!10 (and (not (and (not E) C)) (not K)))
      (a!12 (and (not (and A L)) (not (and (not A) L3))))
      (a!13 (and (not (and A N)) (not (and (not A) M3))))
      (a!14 (and (not (and A P)) (not (and (not A) N3))))
      (a!15 (and (not (and A R)) (not (and (not A) O3))))
      (a!16 (and (not (and A T)) (not (and (not A) P3))))
      (a!17 (and (not (and A V)) (not (and (not A) Q3))))
      (a!18 (and (not (and A X)) (not (and (not A) R3))))
      (a!19 (and (not (and A Z)) (not (and (not A) S3))))
      (a!20 (and (not (and A B1)) (not (and (not A) T3))))
      (a!21 (and (not (and (not Y2) W2)) (not Z2)))
      (a!38 (and (not (and A D1)) (not (and (not A) U3))))
      (a!39 (and (not (and A B)) (not (and (not A) G3)) (not C)))
      (a!41 (and (not (and A D)) (not (and (not A) H3)) (not E)))
      (a!43 (and (not (and A F)) (not (and (not A) I3)) (not G)))
      (a!45 (and (not (and A H)) (not (and (not A) J3)) (not I)))
      (a!47 (and (not (and A J)) (not (and (not A) K3)) (not K)))
      (a!49 (and (not (and A L)) (not (and (not A) L3)) (not M)))
      (a!51 (and (not (and A N)) (not (and (not A) M3)) (not O)))
      (a!53 (and (not (and A P)) (not (and (not A) N3)) (not Q)))
      (a!55 (and (not (and A R)) (not (and (not A) O3)) (not S)))
      (a!57 (and (not (and A T)) (not (and (not A) P3)) (not U)))
      (a!59 (and (not (and A V)) (not (and (not A) Q3)) (not W)))
      (a!61 (and (not (and A X)) (not (and (not A) R3)) (not Y)))
      (a!63 (and (not (and A Z)) (not (and (not A) S3)) (not A1)))
      (a!65 (and (not (and A B1)) (not (and (not A) T3)) (not C1)))
      (a!67 (and (not (and A D1)) (not (and (not A) U3)) (not E1)))
      (a!71 (and (not (and (not O) (not G))) (not (and (not Q) G)) M)))
(let ((a!5 (and (not (and (not E) (not C) K)) (not a!4) E1))
      (a!8 (and (not (and E (not C) G)) (not a!7) E1))
      (a!11 (and (not (and (not E) C I)) (not a!10) E1))
      (a!22 (and (not (and (not C3) A3 (not D3))) (not a!21)))
      (a!23 (and (not (and (not E) (not C) K)) (not a!4) (not B3)))
      (a!24 (and (not (and (not E) (not C) K)) (not a!4)))
      (a!27 (and (not (and (not E) (not C) K)) (not a!4) (not B3) Q))
      (a!30 (and (not (and (not E) (not C) K)) (not a!4) (not X2)))
      (a!33 (and (not (and (not E) (not C) K)) (not a!4) (not X2) Y))
      (a!40 (and (not (and (not a!1) C)) (not a!39)))
      (a!42 (and (not (and (not a!2) E)) (not a!41)))
      (a!44 (and (not (and (not a!3) G)) (not a!43)))
      (a!46 (and (not (and (not a!6) I)) (not a!45)))
      (a!48 (and (not (and (not a!9) K)) (not a!47)))
      (a!50 (and (not (and (not a!12) M)) (not a!49)))
      (a!52 (and (not (and (not a!13) O)) (not a!51)))
      (a!54 (and (not (and (not a!14) Q)) (not a!53)))
      (a!56 (and (not (and (not a!15) S)) (not a!55)))
      (a!58 (and (not (and (not a!16) U)) (not a!57)))
      (a!60 (and (not (and (not a!17) W)) (not a!59)))
      (a!62 (and (not (and (not a!18) Y)) (not a!61)))
      (a!64 (and (not (and (not a!19) A1)) (not a!63)))
      (a!66 (and (not (and (not a!20) C1)) (not a!65)))
      (a!68 (and (not (and (not a!38) E1)) (not a!67))))
(let ((a!25 (and (not a!23) (not (and (not a!24) (not A3))) (not C3) M))
      (a!26 (and (not a!23) (not (and (not a!24) (not A3))) (not C3)))
      (a!28 (and (not (and (not a!24) (not A3))) (not O)))
      (a!31 (and (not a!30) (not (and (not a!24) (not W2))) (not Y2) U))
      (a!32 (and (not a!30) (not (and (not a!24) (not W2))) (not Y2)))
      (a!34 (and (not (and (not a!24) (not W2))) (not W)))
      (a!69 (and (not (and (not a!40)
                           (not a!42)
                           (not a!44)
                           (not a!46)
                           (not a!48)
                           (not a!50)
                           (not a!52)
                           (not a!54)
                           (not a!56)
                           (not a!58)
                           (not a!60)
                           (not a!62)
                           (not a!64)
                           (not a!66)
                           (not a!68)))
                 (not K1))))
(let ((a!29 (and (not a!25)
                 (not (and (not a!26) (not M)))
                 (not a!27)
                 (not (and (not a!23) (not Q)))
                 (not (and (not a!24) (not A3) O))
                 (not a!28)))
      (a!35 (and (not a!31)
                 (not (and (not a!32) (not U)))
                 (not a!33)
                 (not (and (not a!30) (not Y)))
                 (not (and (not a!24) (not W2) W))
                 (not a!34)))
      (a!70 (and (not (and C1 (not S) (not a!69))) (not F1)))
      (a!72 (and (not (and (not a!71) C1 (not a!69))) (not G1)))
      (a!73 (and (not (and (not E) C C1 (not a!69))) (not H1)))
      (a!74 (and (not (and E (not C) C1 (not a!69))) (not I1)))
      (a!75 (and (not (and (not E) (not C) C1 (not a!69))) (not J1))))
(let ((a!36 (and (not (and S (not D3)))
                 (not (and (not a!29) (not S)))
                 (not (and A1 (not Z2)))
                 (not (and (not a!35) (not A1)))
                 C1)))
(let ((a!37 (and (not (and (not a!22) (not E1))) (not (and (not a!36) E1)))))
  (=> (and (Invariant A
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
                K1)
           L1
           (not (= a!1 M1))
           (= N1 F3)
           (not (= a!2 O1))
           (= P1 E3)
           (not (= a!3 Q1))
           (= R1 a!5)
           (not (= a!6 S1))
           (= T1 a!8)
           (not (= a!9 U1))
           (= V1 a!11)
           (not (= a!12 W1))
           (= X1 C3)
           (not (= a!13 Y1))
           (= Z1 A3)
           (not (= a!14 A2))
           (= B2 B3)
           (not (= a!15 C2))
           (= D2 D3)
           (not (= a!16 E2))
           (= F2 Y2)
           (not (= a!17 G2))
           (= H2 W2)
           (not (= a!18 I2))
           (= J2 X2)
           (not (= a!19 K2))
           (= L2 Z2)
           (not (= a!20 M2))
           (= N2 a!37)
           (not (= a!38 O2))
           P2
           (not (= a!70 Q2))
           (not (= a!72 R2))
           (not (= a!73 S2))
           (not (= a!74 T2))
           (not (= a!75 U2))
           (not (= a!69 V2)))
      (Invariant L1
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
           V2)))))))))
(rule (let ((a!1 (and (not (and U3 T3)) (not (and (not U3) O))))
      (a!2 (and (not (and U3 T3)) (not (and (not U3) O)) (not S3)))
      (a!4 (and (not (and U3 R3)) (not (and (not U3) N))))
      (a!5 (and (not (and U3 R3)) (not (and (not U3) N)) (not Q3)))
      (a!7 (and (not (and U3 P3)) (not (and (not U3) M))))
      (a!8 (and (not (and U3 P3)) (not (and (not U3) M)) (not O3)))
      (a!10 (and (not (and U3 N3)) (not (and (not U3) L))))
      (a!11 (and (not (and U3 N3)) (not (and (not U3) L)) (not M3)))
      (a!13 (and (not (and U3 L3)) (not (and (not U3) K))))
      (a!14 (and (not (and U3 L3)) (not (and (not U3) K)) (not K3)))
      (a!16 (and (not (and U3 J3)) (not (and (not U3) J))))
      (a!17 (and (not (and U3 J3)) (not (and (not U3) J)) (not I3)))
      (a!19 (and (not (and U3 H3)) (not (and (not U3) I))))
      (a!20 (and (not (and U3 H3)) (not (and (not U3) I)) (not G3)))
      (a!22 (and (not (and U3 F3)) (not (and (not U3) H))))
      (a!23 (and (not (and U3 F3)) (not (and (not U3) H)) (not E3)))
      (a!25 (and (not (and U3 D3)) (not (and (not U3) G))))
      (a!26 (and (not (and U3 D3)) (not (and (not U3) G)) (not C3)))
      (a!28 (and (not (and U3 B3)) (not (and (not U3) F))))
      (a!29 (and (not (and U3 B3)) (not (and (not U3) F)) (not A3)))
      (a!31 (and (not (and U3 Z2)) (not (and (not U3) E))))
      (a!32 (and (not (and U3 Z2)) (not (and (not U3) E)) (not Y2)))
      (a!34 (and (not (and U3 X2)) (not (and (not U3) D))))
      (a!35 (and (not (and U3 X2)) (not (and (not U3) D)) (not W2)))
      (a!37 (and (not (and U3 V2)) (not (and (not U3) C))))
      (a!38 (and (not (and U3 V2)) (not (and (not U3) C)) (not U2)))
      (a!40 (and (not (and U3 T2)) (not (and (not U3) B))))
      (a!41 (and (not (and U3 T2)) (not (and (not U3) B)) (not S2)))
      (a!43 (and (not (and U3 R2)) (not (and (not U3) A))))
      (a!44 (and (not (and U3 R2)) (not (and (not U3) A)) (not Q2))))
(let ((a!3 (and (not (and (not a!1) S3)) (not a!2)))
      (a!6 (and (not (and (not a!4) Q3)) (not a!5)))
      (a!9 (and (not (and (not a!7) O3)) (not a!8)))
      (a!12 (and (not (and (not a!10) M3)) (not a!11)))
      (a!15 (and (not (and (not a!13) K3)) (not a!14)))
      (a!18 (and (not (and (not a!16) I3)) (not a!17)))
      (a!21 (and (not (and (not a!19) G3)) (not a!20)))
      (a!24 (and (not (and (not a!22) E3)) (not a!23)))
      (a!27 (and (not (and (not a!25) C3)) (not a!26)))
      (a!30 (and (not (and (not a!28) A3)) (not a!29)))
      (a!33 (and (not (and (not a!31) Y2)) (not a!32)))
      (a!36 (and (not (and (not a!34) W2)) (not a!35)))
      (a!39 (and (not (and (not a!37) U2)) (not a!38)))
      (a!42 (and (not (and (not a!40) S2)) (not a!41)))
      (a!45 (and (not (and (not a!43) Q2)) (not a!44))))
  (=> (and (Invariant U3
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
                K2)
           (not a!3)
           (not a!6)
           (not a!9)
           (not a!12)
           (not a!15)
           (not a!18)
           (not a!21)
           (not a!24)
           (not a!27)
           (not a!30)
           (not a!33)
           (not a!36)
           (not a!39)
           (not a!42)
           (not a!45)
           P2
           O2
           N2
           M2
           L2)
      Goal))))
(query Goal)
