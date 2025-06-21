import type { Context } from "hono";
import { StatusCodes } from "http-status-codes";
import { errorResponse, successResponse } from "@/utils/response";
import type { DocumentService } from "@/services/documentService";
import { documentConfig } from "@/config/document";

export const uploadDocument =
  (service: DocumentService) => async (c: Context) => {
    try {
      const body = await c.req.parseBody();
      const file = body.file;
      console.log(file);

      if (
        !file ||
        typeof file !== "object" ||
        !("name" in file) ||
        !("type" in file)
      ) {
        return c.json(
          errorResponse(
            "No valid file provided",
            "BAD_REQUEST",
            StatusCodes.BAD_REQUEST,
          ),
        );
      }
      // Convert File to a Buffer or Uint8Array
      const arrayBuffer = await file.arrayBuffer();
      const data = new Uint8Array(arrayBuffer);

      const typedFile = {
        name: file.name,
        type: file.type,
        data,
      };

      if (!documentConfig.allowedMimeTypes.includes(typedFile.type)) {
        return c.json(
          errorResponse(
            `Unsupported file type: ${typedFile.type}`,
            "BAD_REQUEST",
            StatusCodes.UNSUPPORTED_MEDIA_TYPE,
          ),
        );
      }

      if (typedFile.data.byteLength > documentConfig.maxFileSize) {
        return c.json(
          errorResponse(
            "File too large. Max allowed size is 10MB.",
            "BAD_REQUEST",
            StatusCodes.REQUEST_TOO_LONG,
          ),
        );
      }

      const result = await service.uploadDocument({ file: typedFile });

      return c.json(successResponse(result));
    } catch (err) {
      return c.json(errorResponse("Failed to upload document"));
    }
  };

export const deleteDocument =
  (service: DocumentService) => async (c: Context) => {
    try {
      const id = c.req.param("id");
      if (!id) {
        return c.json(
          errorResponse(
            "No ID provided",
            "BAD_REQUEST",
            StatusCodes.BAD_REQUEST,
          ),
        );
      }

      const result = await service.deleteDocument(id);

      return c.json(successResponse(result));
    } catch (err: unknown) {
      if (err instanceof Error) {
        if (err.message === "Document not found") {
          return c.json(
            errorResponse(err.message, "NOT_FOUND", StatusCodes.NOT_FOUND),
          );
        }

        return c.json(errorResponse("Failed to delete document"));
      }
    }
  };

export const getAllDocuments =
  (service: DocumentService) => async (c: Context) => {
    try {
      const result = await service.getAllDocuments();

      return c.json(successResponse(result));
    } catch (err) {
      return c.json(errorResponse("Failed to fetch documents"));
    }
  };
