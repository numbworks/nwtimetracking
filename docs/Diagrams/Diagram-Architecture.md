```mermaid
classDiagram
  ComponentBag --* TimeTrackingProcessor : __component_bag
  EffortHighlighter --* TTAdapter : __effort_highlighter
  IntHighlighter --* TTAdapter : __int_highlighter
  MomentumManager --* TTDataFrameFactory : __momentum_manager
  SettingBag --* TimeTrackingProcessor : __setting_bag
  TTAdapter --* ComponentBag : tt_adapter
  TTDataFrameFactory --* TTAdapter : __df_factory
  TTDataFrameHelper --* EffortHighlighter : __df_helper
  TTDataFrameHelper --* TTDataFrameFactory : __df_helper
  TTReportManager --* ComponentBag : ttr_manager
```