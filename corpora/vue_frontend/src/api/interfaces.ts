// Interfaces

interface RecordingObject {
  sentence_text: string;
  audio_file_url: string;
  id: number;
}

interface CharVote {
  character: string;
  vote: boolean;
  index: number;
  wordIndex: number;
}

interface CharStructure {
  word: string;
  chars: Array<CharVote>;
}

interface PronunciationJSON {
  ratingSlider: number | null;
  ratingComputed: number;
  characters: Array< Record< string, boolean>>;
}

interface PostRecordingQualityControl {
  good: number;
  bad: number;
  approved: boolean;
  recording: number;
  trash: boolean;
  follow_up: boolean;
  noise: boolean;
  star: number;
  notes: string;
  pronunciation: PronunciationJSON;
  person: number;
}

export {
  RecordingObject,
  CharVote,
  CharStructure,
  PronunciationJSON,
  PostRecordingQualityControl
}
