from apps.calc.machines import ADD
from formlang.utm import UniversalTM, encode, decode

def test_round_trip_encodage():
    M2 = decode(encode(ADD))
    assert M2.run("11+1").tape.count("1") == 3

def test_utm_simule_comme_la_machine():
    desc = encode(ADD)
    U = UniversalTM()
    res_direct = ADD.run("111+11")
    res_utm = U.run(desc, "111+11")
    assert res_utm.tape == res_direct.tape       # U(<M>##w) == M(w)
    assert res_utm.accepted == res_direct.accepted

def test_trace_disponible():
    res = ADD.run("1+1", trace=True)
    assert res.trace and res.trace[0][1] == "q0"
