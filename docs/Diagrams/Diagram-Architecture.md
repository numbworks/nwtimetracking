```mermaid
classDiagram
    %% Relationships
    BYMFactory --> TTDataFrameHelper
    TTDataFrameFactory --> TTDataFrameHelper
    TTMarkdownFactory --> MarkdownHelper
    TTMarkdownFactory --> BYMSplitter
    TTSequencer --> TTDataFrameHelper
    TTAdapter --> TTDataFrameFactory
    TTAdapter --> BYMFactory
    TTAdapter --> TTSequencer
    TTAdapter --> TTMarkdownFactory
    ComponentBag --> TTAdapter
    ComponentBag --> TTLogger
    TTLogger --> SettingSubset
    TimeTrackingProcessor --> ComponentBag
    TimeTrackingProcessor --> SettingBag
    TimeTrackingProcessor --> TTSummary
```