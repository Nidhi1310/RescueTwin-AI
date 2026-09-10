interface ReportActionsProps { content: string; }

export function ReportActions({ content }: ReportActionsProps) {
  const copyReport = async () => {
    await navigator.clipboard.writeText(content);
  };

  const downloadReport = () => {
    const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "rescuetwin-incident-report.txt";
    anchor.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="mt-3 grid grid-cols-2 gap-2">
      <button type="button" onClick={copyReport} className="rounded-md border border-slate-600 px-3 py-2 text-xs font-semibold text-slate-200 hover:bg-slate-800">Copy report</button>
      <button type="button" onClick={downloadReport} className="rounded-md border border-water/40 px-3 py-2 text-xs font-semibold text-water hover:bg-water/10">Download .txt</button>
    </div>
  );
}
