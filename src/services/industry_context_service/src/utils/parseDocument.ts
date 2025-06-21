import { PDFLoader } from "@langchain/community/document_loaders/fs/pdf";
import { DocxLoader } from "@langchain/community/document_loaders/fs/docx";

export async function parseDocument(
	buffer: Buffer | Uint8Array,
	mimeType: string,
): Promise<string> {
	switch (mimeType) {
		case "application/pdf": {
			const loader = new PDFLoader(new Blob([buffer]));
			const docs = await loader.load();
			return docs.map((doc) => doc.pageContent).join("\n");
		}

		case "application/vnd.openxmlformats-officedocument.wordprocessingml.document": {
			const loader = new DocxLoader(new Blob([buffer]));
			const docs = await loader.load();
			return docs.map((doc) => doc.pageContent).join("\n");
		}

		default:
			throw new Error(`Unsupported MIME type: ${mimeType}`);
	}
}
