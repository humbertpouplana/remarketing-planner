from tex_common import *
T=D['p3']['types']; ks=list(T); nm={'applied':'Application submitted','first':'First-step drop-off','fail':'Declined by all lenders','asnef':'Payment-default flag','hq':'High-quality lead','cold':'Cold base'}
ap=T['applied']
tab='\n'.join(f'{nm[k]} & {T[k]["touches"]} & {T[k]["re"]*100:.1f} / {T[k]["rs"]*100:.1f} & {T[k]["tau"]} & {T[k]["V"]:.0f} & {T[k]["L0"]:.0f}\\\\' for k in ks)
res='\n'.join(f'{nm[k]} & {n0(T[k]["net"])} & {T[k]["roi"]:.1f} & {T[k]["ltv"]:.2f} & {T[k]["r24"]*100:.0f}\\% & {T[k]["un"]/10000*100:.0f}\\%\\\\' for k in ks)
st='\n'.join(f'{nm[k]} & {n0(T[k]["net"])} & {n0(T[k]["flat"]["net"])} & {n0(T[k]["agg"]["net"])}\\\\' for k in ks)
rows=ap['rows']; first24=sum(1 for r in rows if r['t']<=1)
sens=dict(D['p3']['sens']); base=D['p3']['base']
abstract=r'''Remarketing to consumer-finance leads is usually run as a set of event-triggered emails with ad hoc timing. We propose a different design principle: spend the contact budget where response decays fastest, which is the first 24 hours, and then space contacts until the lead is considered inactive after 180 days. We formalise a simple response model with exponential decay, a fatigue penalty for recent contacts, channel-specific unsubscribe rates and an incrementality factor, and build a planner that produces a six-month email and SMS calendar for six lead segments derived from an event-based funnel. Under hypothetical but explicit parameters, the front-loaded calendar is never the worst of three calendars (it also beats a constant weekly email in three segments and an aggressive daily cadence in four), and it lifts lifetime value per lead from 11.00 to 11.98 euros in the main segment; the aggressive cadence earns slightly more in the two highest-value segments but at roughly double the unsubscribe rate, a cost the model does not price. Because every response parameter is a hypothesis, the paper's main output is a calendar and a validation design, not an effect size.'''
body=r'''
\section{Introduction}
Lifetime value (LTV) is the value a customer or lead generates over its life \cite{gupta}. For a lead generator, much of that value arrives after the first conversion: a lead who did not complete the application, was declined by every lender, or has a payment-default flag can still convert later through other products. The question is when to contact them and how often. Our operator's experience is that paid remarketing on advertising platforms performs poorly for this business because of low conversion, lower intent on second and third conversions and shorter LTV, and that a well-timed email and SMS flow with a small number of high-quality messages performs better. This paper formalises that approach.

\section{Funnel and segments}
The planner starts from an event-based funnel with the following entry points: a visitor who leaves before signing up; a first-step drop-off; a submitted application; an application declined by all lenders; a lead with a payment-default flag; a high-quality lead (stable income, working-age, permanent contract, no payment-default flag, consumer-credit amount in a defined range, home market only); and a cold list. Messages in the existing funnel are sent at fixed offsets after each event (for example 1 hour, 1 day, 3 days, 6 days after a first step; 1 hour, 2 days, 4 days after an application) and at long intervals thereafter. We retain those anchor times and reshape the rest of the calendar to concentrate contacts early and end at 180 days.

\section{Model}
A cohort of $N$ leads enters a flow at time $0$. Touch $k$ is sent at time $t_k$ days by channel $c_k\in\{\text{email},\text{SMS}\}$. Let $\alpha_k$ be the fraction of the cohort still active before touch $k$ (not converted, not unsubscribed). The model is
\begin{align}
 w(t)&=w_0+(1-w_0)e^{-t/\tau}, & \phi_k&=\frac{1}{1+\gamma\,m_k},\\
 \kappa_k&=\alpha_k\,r_{c_k}\,w(t_k)\,\phi_k, & u_k&=\alpha_k\,\mu_{c_k}\,(1+\eta\,m_k),\\
 \alpha_{k+1}&=\alpha_k-\kappa_k-u_k,
\end{align}
where $\kappa_k$ is the fraction converting at touch $k$, $u_k$ the fraction unsubscribing, $m_k$ the number of touches in the previous 48 hours, $r_c$ the base response of channel $c$, $\tau$ the segment's decay constant (days), $w_0=0.12$ the floor of the decay, $\gamma=0.3$ the fatigue parameter, $\mu_{\text{email}}=0.4\%$, $\mu_{\text{SMS}}=0.9\%$ the unsubscribe rates and $\eta=0.6$. Converted leads stop receiving touches. Incremental revenue is $\sum_k N\kappa_k\,V\,\iota$, with $V$ the value of a conversion and $\iota=0.7$ the incrementality (share of conversions that would not have happened anyway). Cost is $\sum_k N\alpha_k\,q_{c_k}$ with $q=0.003$ euros per email and $0.05$ euros per SMS. Net profit is revenue minus cost and the new LTV per lead is $L_0+\text{net}/N$.

\subsection{Design principle}
Because $w(t)$ decays and fatigue penalises bursts, the marginal value of a touch is highest soon after entry and falls quickly. A calendar that places many touches in the first 24 hours (SMS at 15 minutes, 3 hours and 12 hours; emails at 1 hour and 6 hours, and so on) captures the high-response window. After a week touches are spaced by several days and, after 55 days, by roughly one month, until a final notice and soft unsubscribe at day 180.

\section{Parameters}
Table~\ref{tab:par} gives the segment parameters. They are hypotheses chosen to be plausible and ordered sensibly (high-quality leads respond most, cold lists least); none is measured. Users of the planner can change every value.
\begin{table}[H]\centering\small\caption{Segment parameters: number of touches, base response per send for email / SMS (\%), decay constant $\tau$ (days), conversion value $V$ and baseline LTV $L_0$ (euros).}\label{tab:par}
\begin{tabular}{lrrrrr}\toprule Segment & Touches & Response (\%) & $\tau$ & $V$ & $L_0$\\\midrule
@@PAR@@
\bottomrule\end{tabular}\end{table}

\section{Results}
\subsection{The calendar}
Figure~\ref{fig:tl} shows the calendar for the main segment: @@NT@@ touches, of which @@F24@@ in the first 24 hours; Figure~\ref{fig:bk} shows touches per period.
@@F1@@
@@F2@@
\subsection{Response, fatigue and value}
In this segment @@CONV@@ of the cohort converts, @@UN@@ unsubscribe and @@END@@ remain active at day 180 (Figure~\ref{fig:alive}). @@R24@@ of incremental revenue arrives in the first 24 hours and @@R7@@ within a week, which is the empirical motivation for the front-loaded design. Incremental revenue of @@REV@@ against sending costs of @@COST@@ (Figure~\ref{fig:cum}) gives net profit of @@NET@@ per 10{,}000 leads, a return of @@ROI@@ per euro of cost, and lifts LTV per lead from @@L0@@ to @@LTV@@.
@@F3@@
@@F4@@
\subsection{All segments and alternative calendars}
Table~\ref{tab:res} reports results for every segment. The front-loaded calendar is profitable in four of six segments; the declined and cold-base segments lose money under these parameters, which indicates that they should receive fewer touches or a different offer rather than the same intensity.
\begin{table}[H]\centering\small\caption{Results per 10{,}000 leads: net profit (euros), return on cost, LTV per lead (euros), revenue share in the first 24 hours and share of the cohort that unsubscribes.}\label{tab:res}
\begin{tabular}{lrrrrr}\toprule Segment & Net profit & ROI & LTV/lead & First 24 h & Unsub.\\\midrule
@@RES@@
\bottomrule\end{tabular}\end{table}
We compare the designed calendar against (a) one email per week for 25 weeks and (b) an aggressive schedule of daily emails and SMS every other day for 30 days followed by weekly emails. Table~\ref{tab:strat} and Figure~\ref{fig:strat} show net profit. @@STRATTXT@@
\begin{table}[H]\centering\small\caption{Net profit (euros per 10{,}000 leads) of three calendars.}\label{tab:strat}
\begin{tabular}{lrrr}\toprule Segment & Front-loaded & Weekly email & Aggressive\\\midrule
@@ST@@
\bottomrule\end{tabular}\end{table}
@@F5@@
\subsection{Sensitivity}
Figure~\ref{fig:sens} varies each assumption by $\pm25\%$ for the main segment. Base net profit is @@BASE@@. Response and conversion value are the most influential inputs (@@S1@@ for $+25\%$ response), followed by incrementality; the unsubscribe rate matters less than expected over a six-month horizon, because most conversions occur early.
@@F6@@

\section{Validation design}
Every conclusion above depends on assumed parameters, so the calendar is a starting hypothesis. We recommend a holdout design \cite{kohavi}: randomly withhold a share of each segment (for example 10--20\%) from the flow; measure conversions per lead in treatment and holdout over the horizon, which gives $\iota$ directly; then test cadence variants (front-loaded against weekly) in randomised arms. Primary metric: incremental net profit per lead; guardrails: unsubscribe and spam-complaint rates. The sample needed to detect a difference in conversion rates $p_1,p_2$ is roughly $16\,\bar p(1-\bar p)/(p_1-p_2)^2$ per arm at 80\% power and 5\% significance, which for a difference of one point on a 5\% base is about 7{,}600 leads per arm.

\section{Limitations and compliance}
Parameters are hypotheses and the response model is stylised: no channel interaction, no time-of-day effect, no message content effect, and response is independent across leads. Commercial email and SMS require valid consent and an easy way to opt out; contact outside reasonable hours should be avoided, and regional rules on data protection and electronic communications apply. The planner stops at 180 days, but retaining contact data for longer has its own legal basis requirements.

\section{Conclusion}
A planner built on a small response model produces a transparent, editable calendar that front-loads contacts and expires leads at six months. The front-loaded design is a robust compromise rather than a uniform winner: more intense contact pays only where conversion value is high, and less intense contact wins where it is low. These conclusions come from the model's structure (decay, fatigue, unit costs) and from hypothesised parameters, not from measured effects, so the right next step is a holdout experiment.
'''
refs=r'''\bibitem{gupta} S.~Gupta, D.~Hanssens, B.~Hardie, W.~Kahn, V.~Kumar, N.~Lin, N.~Ravishanker, S.~Sriram. Modeling customer lifetime value. \emph{Journal of Service Research}, 9(2):139--155, 2006.
\bibitem{kohavi} R.~Kohavi, D.~Tang, Y.~Xu. \emph{Trustworthy Online Controlled Experiments}. Cambridge University Press, 2020.'''
better=[k for k in ks if T[k]['net']>T[k]['flat']['net'] and T[k]['net']>T[k]['agg']['net']]
def rep(t):
    d={'PAR':tab,'NT':str(ap['touches']),'F24':str(first24),'CONV':pc(ap['conv']/10000),'UN':pc(ap['un']/10000,0),'END':pc(ap['aliveEnd'],0),'R24':pc(ap['r24'],0),'R7':pc(ap['r7'],0),'REV':E(ap['rev']),'COST':E(ap['cost']),'NET':E(ap['net']),'ROI':f'{ap["roi"]:.1f}','L0':f'{ap["L0"]:.2f}\\,\\texteuro{{}}','LTV':f'{ap["ltv"]:.2f}\\,\\texteuro{{}}',
       'RES':res,'ST':st,'BASE':E(base),'S1':E(sens['Response +25%']-base),
       'STRATTXT':'The front-loaded calendar has the highest net profit in one segment (first-step drop-off), beats the weekly email in three segments and the aggressive schedule in four, and is never the worst of the three. The aggressive schedule earns more in the two segments with the highest conversion value (applied: +2\\%; high quality: +30\\%) but loses between 43\\% and 52\\% of the cohort to unsubscribes, against 12\\% to 22\\% for the front-loaded calendar. The model assigns no cost to a lost contact beyond forgone conversions, so it is biased in favour of aggressive contact. The weekly email wins in the three lowest-value segments (declined, payment-default flag, cold base), where SMS and extra touches do not repay their cost.',
       'F1':fig('p3_timeline','Calendar for the main segment. Shaded area: first 24 hours; the time axis is piecewise linear.').replace('\\caption','\\label{fig:tl}\\caption'),
       'F2':fig('p3_buckets','Touches per lead by period.',"0.8").replace('\\caption','\\label{fig:bk}\\caption'),
       'F3':fig('p3_alive','Share of the cohort active, converted and unsubscribed over time.',"0.8").replace('\\caption','\\label{fig:alive}\\caption'),
       'F4':fig('p3_cum','Cumulative incremental revenue and sending cost.',"0.8").replace('\\caption','\\label{fig:cum}\\caption'),
       'F5':fig('p3_strat','Net profit under three calendars in each segment.',"0.85").replace('\\caption','\\label{fig:strat}\\caption'),
       'F6':fig('p3_sens','Sensitivity of net profit for the main segment.',"0.8").replace('\\caption','\\label{fig:sens}\\caption')}
    for k,v in d.items(): t=t.replace('@@'+k+'@@',v)
    return t
open(ROOT/'paper'/'paper.tex','w').write(make('Remarketing Planner: Front-Loaded Email and SMS Calendars for Lead Lifetime Value','A six-month contact plan for consumer-finance leads',rep(abstract),rep(body),refs))
print(better, {k:(round(T[k]['net']),round(T[k]['flat']['net']),round(T[k]['agg']['net'])) for k in ks})
