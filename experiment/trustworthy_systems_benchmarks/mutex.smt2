(set-option :fp.engine spacer)
(set-logic ALL)
(declare-rel Invariant (Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool Bool))
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
         (not E1))
    (Invariant A B C D E F G H I J K L M N O P Q R S T U V W X Y Z A1 B1 C1 D1 E1)))
(rule (let ((a!1 (not (and (not C) (not D) (not A) (not B))))
      (a!3 (and (not (and A B C D (not M))) B (not (and A B (not C) (not D)))))
      (a!6 (and (not (and A B C D M)) D (not (and C D (not A) (not B)))))
      (a!8 (and (not (and (not A) B)) (not (and (not C) D))))
      (a!10 (and (not (and G H)) (not (and (not G) Q2))))
      (a!11 (and (not (and G I)) (not (and (not G) R2))))
      (a!12 (and (not (and G J)) (not (and (not G) S2))))
      (a!13 (and (not (and G K)) (not (and (not G) T2))))
      (a!14 (and (not (and G L)) (not (and (not G) U2))))
      (a!15 (and (not (and A B (not C) (not D))) M))
      (a!17 (and (not (and G N)) (not (and (not G) V2))))
      (a!18 (and (not (and G P)) (not (and (not G) W2))))
      (a!19 (and (not (and G R)) (not (and (not G) X2))))
      (a!20 (and (not (and G T)) (not (and (not G) Y2))))
      (a!21 (and (not (and G V)) (not (and (not G) Z2))))
      (a!22 (and (not (and G X)) (not (and (not G) A3))))
      (a!23 (and (not (and G Z)) (not (and (not G) B3))))
      (a!24 (and (not (and (not P2) (not O2))) (not (and (not M2) L2))))
      (a!37 (and (not (and G B1)) (not (and (not G) C3))))
      (a!38 (and (not (and G H)) (not (and (not G) Q2)) (not B)))
      (a!40 (and (not (and G I)) (not (and (not G) R2)) (not A)))
      (a!42 (and (not (and G J)) (not (and (not G) S2)) (not D)))
      (a!44 (and (not (and G K)) (not (and (not G) T2)) (not C)))
      (a!46 (and (not (and G L)) (not (and (not G) U2)) (not M)))
      (a!48 (and (not (and G N)) (not (and (not G) V2)) (not O)))
      (a!50 (and (not (and G P)) (not (and (not G) W2)) (not Q)))
      (a!52 (and (not (and G R)) (not (and (not G) X2)) (not S)))
      (a!54 (and (not (and G T)) (not (and (not G) Y2)) (not U)))
      (a!56 (and (not (and G V)) (not (and (not G) Z2)) (not W)))
      (a!58 (and (not (and G X)) (not (and (not G) A3)) (not Y)))
      (a!60 (and (not (and G Z)) (not (and (not G) B3)) (not A1)))
      (a!62 (and (not (and G B1)) (not (and (not G) C3)) (not E)))
      (a!66 (and (not (and A (not B))) (not Q) A B)))
(let ((a!2 (and (not (and A B C D (not M)))
                (not (and A B))
                (not (and A B (not C) (not D)))
                (not (and C (not D) (not A) (not B)))
                a!1
                (not (and C D (not A) (not B)))))
      (a!4 (and (not (and C D (not A) (not B)))
                (not a!3)
                (not (and C (not D) (not A) (not B)))
                a!1))
      (a!5 (and (not (and A B C D M))
                (not (and C D))
                (not (and C D (not A) (not B)))
                (not (and A (not B) (not C) (not D)))
                a!1
                (not (and A B (not C) (not D)))))
      (a!7 (and (not a!6)
                (not (and A (not B) (not C) (not D)))
                a!1
                (not (and A B (not C) (not D)))))
      (a!9 (and (not (and (not a!8) E)) (not F)))
      (a!16 (and (not a!15) (not (and C D (not A) (not B)))))
      (a!25 (and (not (and A B C D (not M)))
                 (not (and A B))
                 (not (and A B (not C) (not D)))
                 (not (and C (not D) (not A) (not B)))
                 a!1))
      (a!39 (and (not (and (not a!10) B)) (not a!38)))
      (a!41 (and (not (and (not a!11) A)) (not a!40)))
      (a!43 (and (not (and (not a!12) D)) (not a!42)))
      (a!45 (and (not (and (not a!13) C)) (not a!44)))
      (a!47 (and (not (and (not a!14) M)) (not a!46)))
      (a!49 (and (not (and (not a!17) O)) (not a!48)))
      (a!51 (and (not (and (not a!18) Q)) (not a!50)))
      (a!53 (and (not (and (not a!19) S)) (not a!52)))
      (a!55 (and (not (and (not a!20) U)) (not a!54)))
      (a!57 (and (not (and (not a!21) W)) (not a!56)))
      (a!59 (and (not (and (not a!22) Y)) (not a!58)))
      (a!61 (and (not (and (not a!23) A1)) (not a!60)))
      (a!63 (and (not (and (not a!37) E)) (not a!62))))
(let ((a!26 (and (not a!25)
                 (not (and C D (not A) (not B)))
                 (not a!3)
                 (not (and C (not D) (not A) (not B)))
                 a!1))
      (a!64 (and (not (and (not a!39)
                           (not a!41)
                           (not a!43)
                           (not a!45)
                           (not a!47)
                           (not a!49)
                           (not a!51)
                           (not a!53)
                           (not a!55)
                           (not a!57)
                           (not a!59)
                           (not a!61)
                           (not a!63)))
                 (not E1))))
(let ((a!27 (not (and (not a!26) (not N2) (not a!2) (not a!4))))
      (a!29 (and (not (and (not a!26) (not N2))) (not Q)))
      (a!31 (not (and (not a!2) (not a!4) (not a!26) (not K2))))
      (a!33 (and (not (and (not a!26) (not K2))) (not W)))
      (a!65 (and (not (and A1 (not S) (not a!64))) (not C1)))
      (a!67 (and (not (and (not a!66) O)) A1 (not a!64))))
(let ((a!28 (and (not (and a!27 (not O2))) (not O)))
      (a!32 (and (not (and a!31 (not L2))) (not U)))
      (a!68 (not (= (and (not a!67) (not D1)) I2))))
(let ((a!30 (and (not (and a!27 (not O2) O))
                 (not a!28)
                 (not (and (not a!26) (not N2) Q))
                 (not a!29)))
      (a!34 (and (not (and a!31 (not L2) U))
                 (not a!32)
                 (not (and (not a!26) (not K2) W))
                 (not a!33))))
(let ((a!35 (and (not (and S (not P2)))
                 (not (and (not a!30) (not S)))
                 (not (and Y (not M2)))
                 (not (and (not a!34) (not Y)))
                 A1)))
(let ((a!36 (and (not (and (not a!24) (not E))) (not (and (not a!35) E)))))
(let ((a!69 (and (Invariant A
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
                      E1)
                 (= F1 (and (not a!2) E))
                 (= G1 (and (not a!4) E))
                 (= H1 (and (not a!5) E))
                 (= I1 (and (not a!7) E))
                 J1
                 (not (= a!9 K1))
                 L1
                 (not (= a!10 M1))
                 (not (= a!11 N1))
                 (not (= a!12 O1))
                 (not (= a!13 P1))
                 (not (= a!14 Q1))
                 (= R1 (and (not a!16) E))
                 (not (= a!17 S1))
                 (= T1 O2)
                 (not (= a!18 U1))
                 (= V1 N2)
                 (not (= a!19 W1))
                 (= X1 P2)
                 (not (= a!20 Y1))
                 (= Z1 L2)
                 (not (= a!21 A2))
                 (= B2 K2)
                 (not (= a!22 C2))
                 (= D2 M2)
                 (not (= a!23 E2))
                 (= F2 a!36)
                 (not (= a!37 G2))
                 (not (= a!65 H2))
                 a!68
                 (not (= a!64 J2)))))
  (=> a!69
      (Invariant F1
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
           J2))))))))))))
(rule (let ((a!1 (and (not (and (not C3) B3)) (not (and (not A3) Z2))))
      (a!2 (and (not (and W2 V2)) (not (and (not W2) M))))
      (a!3 (and (not (and W2 V2)) (not (and (not W2) M)) (not B3)))
      (a!5 (and (not (and W2 U2)) (not (and (not W2) L))))
      (a!6 (and (not (and W2 U2)) (not (and (not W2) L)) (not C3)))
      (a!8 (and (not (and W2 T2)) (not (and (not W2) K))))
      (a!9 (and (not (and W2 T2)) (not (and (not W2) K)) (not Z2)))
      (a!11 (and (not (and W2 S2)) (not (and (not W2) J))))
      (a!12 (and (not (and W2 S2)) (not (and (not W2) J)) (not A3)))
      (a!14 (and (not (and W2 R2)) (not (and (not W2) I))))
      (a!15 (and (not (and W2 R2)) (not (and (not W2) I)) (not Q2)))
      (a!17 (and (not (and W2 P2)) (not (and (not W2) H))))
      (a!18 (and (not (and W2 P2)) (not (and (not W2) H)) (not O2)))
      (a!20 (and (not (and W2 N2)) (not (and (not W2) G))))
      (a!21 (and (not (and W2 N2)) (not (and (not W2) G)) (not M2)))
      (a!23 (and (not (and W2 L2)) (not (and (not W2) F))))
      (a!24 (and (not (and W2 L2)) (not (and (not W2) F)) (not K2)))
      (a!26 (and (not (and W2 J2)) (not (and (not W2) E))))
      (a!27 (and (not (and W2 J2)) (not (and (not W2) E)) (not I2)))
      (a!29 (and (not (and W2 H2)) (not (and (not W2) D))))
      (a!30 (and (not (and W2 H2)) (not (and (not W2) D)) (not G2)))
      (a!32 (and (not (and W2 F2)) (not (and (not W2) C))))
      (a!33 (and (not (and W2 F2)) (not (and (not W2) C)) (not E2)))
      (a!35 (and (not (and W2 D2)) (not (and (not W2) B))))
      (a!36 (and (not (and W2 D2)) (not (and (not W2) B)) (not C2)))
      (a!38 (and (not (and W2 B2)) (not (and (not W2) A))))
      (a!39 (and (not (and W2 B2)) (not (and (not W2) A)) (not Y2))))
(let ((a!4 (and (not (and (not a!2) B3)) (not a!3)))
      (a!7 (and (not (and (not a!5) C3)) (not a!6)))
      (a!10 (and (not (and (not a!8) Z2)) (not a!9)))
      (a!13 (and (not (and (not a!11) A3)) (not a!12)))
      (a!16 (and (not (and (not a!14) Q2)) (not a!15)))
      (a!19 (and (not (and (not a!17) O2)) (not a!18)))
      (a!22 (and (not (and (not a!20) M2)) (not a!21)))
      (a!25 (and (not (and (not a!23) K2)) (not a!24)))
      (a!28 (and (not (and (not a!26) I2)) (not a!27)))
      (a!31 (and (not (and (not a!29) G2)) (not a!30)))
      (a!34 (and (not (and (not a!32) E2)) (not a!33)))
      (a!37 (and (not (and (not a!35) C2)) (not a!36)))
      (a!40 (and (not (and (not a!38) Y2)) (not a!39))))
(let ((a!41 (and (Invariant C3
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
                 (not (and (not a!1) Y2))
                 (not X2)
                 (not a!4)
                 (not a!7)
                 (not a!10)
                 (not a!13)
                 (not a!16)
                 (not a!19)
                 (not a!22)
                 (not a!25)
                 (not a!28)
                 (not a!31)
                 (not a!34)
                 (not a!37)
                 (not a!40)
                 A2
                 Z1)))
  (=> a!41 Goal)))))
(query Goal)
