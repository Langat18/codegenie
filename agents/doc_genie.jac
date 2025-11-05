"""DocGenie Agent - Generates documentation"""
import:py os;
import:py datetime;

walker DocGenie {
    has output_dir: str = "./outputs";
    
    can start with Repository entry {
        print(f"[DocGenie] Generating documentation");
        file_tree = [-->(`?FileTree)][0] if [-->(`?FileTree)] else None;
        readme = [-->(`?ReadmeSummary)][0] if [-->(`?ReadmeSummary)] else None;
        ccg = [-->(`?CodeContextGraph)][0] if [-->(`?CodeContextGraph)] else None;
        
        if not ccg:
            return;
        
        doc = Documentation();
        here ++> doc;
        doc.markdown = self._build_markdown(here.name, file_tree, readme, ccg);
        doc.diagrams = self._create_diagrams(ccg);
        self._save_doc(here.name, doc);
        visit doc;
    }
    
    can finalize with Documentation entry {
        print(f"[DocGenie] Saved to {here.output_path}");
        report {"status": "success", "output_path": here.output_path};
    }
    
    def _build_markdown(repo_name: str, file_tree, readme, ccg) -> str {
        sections = [];
        sections.append(f"# {repo_name}\n");
        sections.append(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d')}\n\n");
        sections.append("## Overview\n\n");
        if readme and readme.found:
            sections.append(readme.summary + "\n\n");
        if file_tree:
            sections.append(f"## Structure\n\n- Files: {file_tree.total_files}\n\n");
        sections.append("## Components\n\n");
        if ccg.classes:
            sections.append("### Classes\n\n");
            for key, cls in list(ccg.classes.items())[:10]:
                sections.append(f"#### `{cls['name']}`\n*File: {os.path.basename(cls['file'])}*\n\n");
        return "".join(sections);
    }
    
    def _create_diagrams(ccg) -> list {
        diagrams = [];
        if ccg.classes:
            mermaid = ["```mermaid", "classDiagram"];
            for key, cls in list(ccg.classes.items())[:5]:
                mermaid.append(f"    class {cls['name']}");
            mermaid.append("```");
            diagrams.append(("Class Diagram", "\n".join(mermaid)));
        return diagrams;
    }
    
    def _save_doc(repo_name: str, doc) -> None {
        os.makedirs(self.output_dir, exist_ok=True);
        output_path = os.path.join(self.output_dir, f"{repo_name}_docs.md");
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(doc.markdown);
            if doc.diagrams:
                for title, diagram in doc.diagrams:
                    f.write(f"\n## {title}\n\n{diagram}\n");
        doc.output_path = output_path;
    }
}
