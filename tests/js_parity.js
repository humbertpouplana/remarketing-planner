const fs = require('fs');
const html = fs.readFileSync(process.argv[2], 'utf8');
const PARAMS = JSON.parse(html.match(/const PARAMS = (\{.*?\});\n/s)[1]);
const calc = html.split('/*CALC*/')[1].split('/*ENDCALC*/')[0];
const f = new Function('PARAMS', 'const DEF0=1;' + calc + ';return {simulate,summarize,revShare,flatSched,aggSched,pools,DEF};')(PARAMS);
const N = PARAMS.cohort, out = {};
for (const [k, T] of Object.entries(PARAMS.types)) {
  const P = {...f.DEF, re: T.re, rs: T.rs, tau: T.tau, V: T.V, kR: PARAMS.response_multiplier, inc: PARAMS.incrementality, ce: PARAMS.cost_email, cs: PARAMS.cost_sms};
  const rows = f.simulate(P, T.sched.map(x => x.slice()));
  out[k] = {net: f.summarize(rows, N).net, r24: f.revShare(rows, 1), flat: f.summarize(f.simulate(P, f.flatSched()), N).net, agg: f.summarize(f.simulate(P, f.aggSched()), N).net};
}
console.log(JSON.stringify(out));
