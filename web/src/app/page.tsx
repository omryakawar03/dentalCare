const nav = [
  { title: "WORKSPACE", items: [["⌂", "Overview"], ["▦", "Schedule"], ["♙", "Patients"], ["✚", "Clinical"]] },
  { title: "OPERATIONS", items: [["₹", "Finance"], ["▤", "Inventory"], ["✉", "Inbox"], ["⌁", "Insights"]] },
  { title: "MANAGE", items: [["◉", "Team"], ["⚙", "Settings"]] },
];
const appName = process.env.NEXT_PUBLIC_APP_NAME ?? "DentalCare";

const metrics = [
  ["Appointments today", "—", "Schedule data will appear here", "▦"],
  ["Collections today", "—", "Payments recorded today", "₹"],
  ["Outstanding balance", "—", "Open patient invoices", "◷"],
  ["Follow-ups due", "—", "Patients to contact", "↗"],
];

export default function Home() {
  return <div className="shell">
    <aside className="sidebar">
      <div className="brand"><span className="brand-mark">✦</span><span>{appName}</span></div>
      {nav.map((group) => <section key={group.title}>
        <div className="nav-label">{group.title}</div>
        {group.items.map(([icon, label], index) => <a key={label} className={`nav-link ${group.title === "WORKSPACE" && index === 0 ? "active" : ""}`} href="#">
          <span className="nav-icon">{icon}</span>{label}
        </a>)}
      </section>)}
      <div className="sidebar-foot"><span className="avatar">DS</span><div><strong style={{fontSize:12}}>Clinic owner</strong><div className="muted">Practice administrator</div></div></div>
    </aside>
    <main className="main">
      <header className="topbar"><button className="clinic-select">All clinics　⌄</button><div className="top-actions"><button aria-label="Notifications" className="icon-button">♧</button><span className="avatar">DS</span></div></header>
      <div className="content">
        <div className="page-head"><div><div className="eyebrow">Monday · Clinic overview</div><h1>Good morning</h1><div className="subtitle">Here’s what needs your attention across your practice today.</div></div><button className="button-primary">＋ New appointment</button></div>
        <section className="metrics" aria-label="Today's metrics">{metrics.map(([label, value, note, icon]) => <article className="metric" key={label}>
          <div className="metric-top"><span>{label}</span><span className="metric-icon">{icon}</span></div><div className="metric-value">{value}</div><div className="metric-note">{note}</div>
        </article>)}</section>
        <section className="dashboard-grid">
          <article className="panel"><div className="panel-head"><div><div className="panel-title">Revenue overview</div><div className="panel-subtitle">Collections across selected clinics</div></div><a className="panel-link" href="#">View report →</a></div><div className="empty-state"><span className="empty-symbol">⌁</span><span>Financial activity will appear when connected.</span></div></article>
          <article className="panel"><div className="panel-head"><div><div className="panel-title">Today’s schedule</div><div className="panel-subtitle">Appointments and patient queue</div></div><a className="panel-link" href="#">Open schedule →</a></div><div className="empty-state"><span className="empty-symbol">▦</span><span>No schedule data yet</span></div></article>
        </section>
        <section className="bottom-grid">
          <article className="panel"><div className="panel-title">Needs attention</div><div className="panel-subtitle">Items requiring follow-up</div><div className="attention"><span className="attention-dot"/>Pending payments<span className="attention-count">—</span></div><div className="attention"><span className="attention-dot calm"/>Patient follow-ups<span className="attention-count">—</span></div><div className="attention"><span className="attention-dot"/>Low stock & expiry<span className="attention-count">—</span></div></article>
          <article className="panel"><div className="panel-head"><div><div className="panel-title">Clinic comparison</div><div className="panel-subtitle">Current month · actual figures</div></div><a className="panel-link" href="#">Compare →</a></div><div className="empty-state"><span>Clinic performance will appear here.</span></div></article>
          <article className="panel"><div className="panel-title">Quick actions</div><div className="panel-subtitle">Common tasks</div><div className="attention"><span className="metric-icon">♙</span>Register patient</div><div className="attention"><span className="metric-icon">▦</span>Book appointment</div><div className="attention"><span className="metric-icon">₹</span>Record payment</div></article>
        </section>
      </div>
    </main>
  </div>;
}
