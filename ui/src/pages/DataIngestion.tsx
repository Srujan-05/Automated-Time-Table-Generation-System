
import React, { useState } from "react";
import { UploadSimple, FileCsv, CheckCircle } from "@phosphor-icons/react";
import { motion } from "framer-motion";
import type { FileUpload } from "../lib/types";

const DataIngestion = () => {
   const [dragActive, setDragActive] = useState<boolean>(false);
   const [files, setFiles] = useState<FileUpload[]>([]);

   const handleDrag = (e: React.DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      e.stopPropagation();
      if (e.type === "dragenter" || e.type === "dragover") {
         setDragActive(true);
      } else if (e.type === "dragleave") {
         setDragActive(false);
      }
   };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
       // Mock file upload
       const newFile: FileUpload = { name: e.dataTransfer.files[0].name, status: "uploading" };
       setFiles(prev => [...prev, newFile]);
       setTimeout(() => {
          setFiles(prev => prev.map(f => f.name === newFile.name ? { ...f, status: "completed" } : f));
       }, 2000);
    }
  };

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      <div className="flex items-center justify-between">
         <h1 className="text-3xl font-bold text-white tracking-tight">Data Ingestion</h1>
         <div className="flex gap-2">
            <button className="px-4 py-2 bg-zinc-800 text-zinc-300 rounded-lg text-sm hover:bg-zinc-700 transition-colors">Download Template</button>
            <button className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm hover:bg-red-700 transition-colors shadow-lg shadow-red-500/20">Import Data</button>
         </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
         {["Courses", "Faculty", "Rooms"].map((type) => (
            <div key={type} className="bg-zinc-900/40 border border-zinc-800/50 p-6 rounded-2xl hover:border-red-500/30 transition-all cursor-pointer group">
               <div className="flex items-center justify-between mb-4">
                  <h3 className="font-medium text-white">{type} CSV</h3>
                  <FileCsv className="w-6 h-6 text-zinc-500 group-hover:text-red-500 transition-colors" />
               </div>
               <p className="text-xs text-zinc-500">Required fields: ID, Name, Capacity...</p>
            </div>
         ))}
      </div>

      <motion.div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        animate={{ scale: dragActive ? 1.02 : 1, borderColor: dragActive ? "#ef4444" : "#27272a" }}
        className={`
          relative border-2 border-dashed rounded-3xl p-12 text-center transition-all duration-300
          ${dragActive ? "bg-red-500/5" : "bg-zinc-900/20"}
        `}
      >
        <div className="pointer-events-none flex flex-col items-center gap-4">
           <div className="p-4 rounded-full bg-zinc-800 text-zinc-400 mb-2">
              <UploadSimple className="w-8 h-8" />
           </div>
           <h3 className="text-xl font-bold text-white">Drag & drop your CSV files here</h3>
           <p className="text-zinc-500">or click to browse from your computer</p>
        </div>
      <input 
         type="file" 
         className="absolute inset-0 w-full h-full opacity-0 cursor-pointer" 
         onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
            const file = e.target.files && e.target.files[0];
            if (file) {
               const newFile: FileUpload = { name: file.name, status: "uploading" };
               setFiles(prev => [...prev, newFile]);
               setTimeout(() => {
                  setFiles(prev => prev.map(f => f.name === newFile.name ? { ...f, status: "completed" } : f));
               }, 2000);
            }
         }}
      />
      </motion.div>

      {/* File List */}
      <div className="space-y-3">
         {files.map((file, i) => (
            <motion.div 
                key={i}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center justify-between p-4 bg-zinc-900/50 border border-zinc-800 rounded-xl"
            >
               <div className="flex items-center gap-3">
                  <FileCsv className="w-5 h-5 text-red-500" />
                  <span className="text-white font-mono text-sm">{file.name}</span>
               </div>
               {file.status === "uploading" ? (
                  <div className="flex items-center gap-2 text-zinc-500 text-xs uppercase font-bold tracking-wider">
                     <span className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse" />
                     Uploading...
                  </div>
               ) : (
                  <div className="flex items-center gap-2 text-green-500 text-xs uppercase font-bold tracking-wider">
                     <CheckCircle weight="fill" className="w-4 h-4" />
                     Completed
                  </div>
               )}
            </motion.div>
         ))}
      </div>
    </div>
  );
};

export default DataIngestion;
