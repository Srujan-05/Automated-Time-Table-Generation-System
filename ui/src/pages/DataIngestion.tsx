import { Button } from "@/components/ui/button";
import { IngestionCard } from "@/components/ingestion/IngestionCard";
import { FileUploadZone } from "@/components/ingestion/FileUploadZone";
import { FileList } from "@/components/ingestion/FileList";
import { useIngestion } from "@/hooks/useIngestion";
import { Spinner } from "@/components/common/Spinner";

const DataIngestion = () => {
   const { 
    dragActive, 
    files, 
    handleDrag, 
    handleDrop, 
    handleFileChange, 
    handleSeed, 
    isImporting, 
    ingestionTypes 
   } = useIngestion();

  return (
    <div className="space-y-8 max-w-4xl mx-auto pb-12">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
         <div>
          <h1 className="text-3xl font-bold text-foreground tracking-tight">Data Ingestion</h1>
          <p className="text-muted-foreground text-sm">Upload CSV templates to populate the system database.</p>
         </div>
         <div className="flex gap-2">
            <Button 
                variant="outline" 
                className="h-12 px-6 rounded-xl font-medium"
                onClick={() => {
                  const link = document.createElement('a');
                  link.href = `http://localhost:5000/api/ingestion/templates`;
                  link.download = 'timetable_templates.zip';
                  document.body.appendChild(link);
                  link.click();
                  document.body.removeChild(link);
                }}
            >
              Download Templates (.zip)
            </Button>
            <Button 
                onClick={handleSeed} 
                disabled={isImporting}
                className="h-12 px-6 rounded-xl font-medium shadow-lg shadow-primary/20"
            >
                {isImporting ? <Spinner /> : null}
                Seed Data
            </Button>
         </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
         {ingestionTypes.map((item) => (
            <IngestionCard key={item.type} {...item} />
         ))}
      </div>

      <FileUploadZone 
        dragActive={dragActive}
        onDrag={handleDrag}
        onDrop={handleDrop}
        onFileChange={handleFileChange}
      />

      <FileList files={files} />
    </div>
  );
};

export default DataIngestion;
