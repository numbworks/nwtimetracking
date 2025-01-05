```mermaid
classDiagram
  BYMFactory --* TTAdapter
  BYMSplitter --* TTAdapter
  ComponentBag --* TimeTrackingProcessor
  EffortHighlighter --* TTAdapter
  SettingBag --* TimeTrackingProcessor
  TTAdapter --* ComponentBag
  TTDataFrameFactory --* TTAdapter
  TTDataFrameHelper --* BYMFactory
  TTDataFrameHelper --* BYMSplitter
  TTDataFrameHelper --* EffortHighlighter
  TTDataFrameHelper --* TTDataFrameFactory
  TTDataFrameHelper --* TTSequencer
  TTLogger --* ComponentBag
  TTMarkdownFactory --* TTAdapter
  TTSequencer --* TTAdapter
```