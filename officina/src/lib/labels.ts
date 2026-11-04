import type { CommessaStatus } from "./data/types";
import type { Tone } from "@/components/ui/Badge";

export const COMMESSA_STATUS_LABEL: Record<CommessaStatus, string> = {
  inserita: "Bozza", in_corso: "Aperta", in_attesa: "Sospesa", chiusa: "Chiusa", annullata: "Annullata",
};
export const COMMESSA_STATUS_TONE: Record<CommessaStatus, Tone> = {
  inserita: "neutral", in_corso: "info", in_attesa: "warning", chiusa: "success", annullata: "danger",
};
