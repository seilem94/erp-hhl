export function Hero() {
  return (
    <section aria-labelledby="home-title" className="dashboard-hero relative isolate overflow-hidden">
      <div className="page-container relative py-14 sm:py-20 lg:py-23">
        <img src="/hero-blueprint.svg" alt="" width="480" height="360" className="pointer-events-none absolute -right-16 top-5 -z-10 hidden h-88 w-120 opacity-70 lg:block" />
        <div className="max-w-2xl">
          <p className="inline-flex items-center gap-2.5 rounded-full border border-blue-200/70 bg-white/80 px-3.5 py-1.5 text-[11px] font-semibold tracking-[0.14em] text-brand-blue">
            <span className="size-1.5 rounded-full bg-brand-blue" /> HHL ERP
          </p>
          <h1 id="home-title" className="mt-6 text-[2.5rem] leading-[1.12] font-semibold tracking-[-0.045em] sm:text-[3.5rem] lg:text-[3.75rem]">
            Gestión de obras <span className="block text-brand-blue">y gastos</span>
          </h1>
          <p className="mt-6 max-w-xl text-[15px] leading-7 text-slate-500 sm:text-base sm:leading-8">
            Control operativo en terreno y administración financiera de proyectos eléctricos.
            Un espacio para organizar las obras y los gastos de tu equipo.
          </p>
        </div>
      </div>
    </section>
  )
}
