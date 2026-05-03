import { useState } from "react";
import { toast } from "sonner";
import type { FileUpload } from "@/lib/types";
import { api } from "@/lib/api";

export const useIngestion = () => {
  const [dragActive, setDragActive] = useState<boolean>(false);
  const [files, setFiles] = useState<FileUpload[]>([]);
  const [isImporting, setIsImporting] = useState(false);
  
  const ingestionTypes = [
    { type: "Courses", description: "Required fields: course_code, session_type, professor, student_group" },
    { type: "Faculty", description: "Required fields: name, email (optional)" },
    { type: "Rooms", description: "Required fields: name, is_lab, capacity. Optional: allowed_batches (JSON list of batch names)" },
  ];

  const handleDrag = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const processFiles = async (fileList: FileList | null) => {
    if (!fileList) return;
    
    const fileArray = Array.from(fileList);
    for (const file of fileArray) {
      const newFile: FileUpload = { name: file.name, status: "uploading" };
      setFiles(prev => [...prev, newFile]);
      
      try {
        // Simple heuristic to determine type from filename
        let type = "courses";
        if (file.name.toLowerCase().includes("faculty") || file.name.toLowerCase().includes("prof")) type = "faculties";
        else if (file.name.toLowerCase().includes("room")) type = "rooms";
        
        await api.ingestion.uploadFile(type, file);
        
        setFiles(prev => prev.map(f => 
          f.name === file.name ? { ...f, status: "completed" } : f
        ));
        toast.success(`${file.name} processed as ${type}`);
      } catch (err) {
        console.error("Upload failed", err);
        toast.error(`Failed to upload ${file.name}`);
        setFiles(prev => prev.filter(f => f.name !== file.name));
      }
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    processFiles(e.dataTransfer.files);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    processFiles(e.target.files);
  };

  const handleSeed = async () => {
    setIsImporting(true);
    try {
        const res = await api.ingestion.triggerSeed();
        toast.success(`Database seeded: ${res.professors_added} professors, ${res.rooms_added} rooms, ${res.instances_created} instances`);
        setFiles([]);
    } catch (err) {
        toast.error("Failed to seed database");
        console.error(err);
    } finally {
        setIsImporting(false);
    }
  };

  return {
    dragActive,
    files,
    handleDrag,
    handleDrop,
    handleFileChange,
    handleSeed,
    isImporting,
    ingestionTypes
  };
};
