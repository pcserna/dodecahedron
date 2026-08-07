import sqlite3
conn = sqlite3.connect("database/rdorp.sqlite")

print("=== CORPUS ===")
total = conn.execute("SELECT COUNT(*) FROM specimens").fetchone()[0]
measured = conn.execute("SELECT COUNT(*) FROM specimens WHERE max_diameter_mm IS NOT NULL OR weight_g IS NOT NULL").fetchone()[0]
print(f"Total specimens: {total}")
print(f"With measurements: {measured}")
print(f"Observations total: {conn.execute('SELECT COUNT(*) FROM artifact_observations').fetchone()[0]}")

print()
print(f"{'EV':<6} {'Variable':<32} {'Power':<12} {'obs':>4} {'spec':>5}")
print("-" * 62)
for r in conn.execute("""
    SELECT ev.ev_id, ev.variable, ev.discriminatory_power,
           COUNT(o.observation_id) n_obs,
           COUNT(DISTINCT o.rd_id) n_spec
    FROM evidence_variables ev
    LEFT JOIN artifact_observations o ON ev.ev_id = o.ev_id
    GROUP BY ev.ev_id
    ORDER BY CASE ev.discriminatory_power
        WHEN 'Very High' THEN 1 WHEN 'High' THEN 2 ELSE 3 END, ev.ev_id
"""):
    ev, var, power, n_obs, n_spec = r
    flag = " <<" if (power == "Very High" and n_spec < 3) else ""
    print(f"{ev:<6} {var[:32]:<32} {(power or ''):<12} {n_obs:>4} {n_spec:>5}{flag}")

print()
print("=== VERY HIGH PRIORITY VARIABLES — COVERAGE ===")
for r in conn.execute("""
    SELECT ev.ev_id, ev.variable, COUNT(DISTINCT o.rd_id) n
    FROM evidence_variables ev
    LEFT JOIN artifact_observations o ON ev.ev_id = o.ev_id
    WHERE ev.discriminatory_power = 'Very High'
    GROUP BY ev.ev_id ORDER BY n DESC
"""):
    bar = "#" * r[2]
    print(f"  {r[0]} {r[1][:35]:<35} {r[2]:>2} {bar}")

print()
print("=== CONTEXT & WEAR COVERAGE (key for hypothesis discrimination) ===")
for cat in ["Context", "Wear"]:
    rows = conn.execute("""
        SELECT ev.ev_id, ev.variable, ev.discriminatory_power, COUNT(DISTINCT o.rd_id) n
        FROM evidence_variables ev
        LEFT JOIN artifact_observations o ON ev.ev_id = o.ev_id
        WHERE ev.category = ?
        GROUP BY ev.ev_id ORDER BY ev.ev_id
    """, (cat,)).fetchall()
    print(f"  {cat}:")
    for r in rows:
        print(f"    {r[0]} {r[1][:30]:<30} [{r[2]:<9}] n={r[3]}")

print()
print("=== SPECIMENS WITH CONTEXT DATA (EV025 site type) ===")
for r in conn.execute("""
    SELECT s.rd_id, s.specimen_name, o.observed_value
    FROM specimens s
    JOIN artifact_observations o ON s.rd_id = o.rd_id AND o.ev_id = 'EV025'
    ORDER BY s.rd_id
"""):
    print(f"  {r[0]}  {r[1][:35]:<35}  {(r[2] or '')[:50]}")

print()
print("=== WEAR OBSERVATIONS (EV017 internal, EV018 external, EV019 rope, EV023 thermal) ===")
for ev in ["EV017", "EV018", "EV019", "EV023"]:
    rows = conn.execute("""
        SELECT s.rd_id, o.observed_value, o.confidence
        FROM artifact_observations o JOIN specimens s ON s.rd_id=o.rd_id
        WHERE o.ev_id = ?
    """, (ev,)).fetchall()
    var = conn.execute("SELECT variable FROM evidence_variables WHERE ev_id=?", (ev,)).fetchone()[0]
    print(f"  {ev} {var}: {len(rows)} obs")
    for r in rows:
        print(f"    {r[0]}: [{r[2]}] {(r[1] or '')[:70]}")

conn.close()
