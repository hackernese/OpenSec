"missbugs": [
    df_results["Claude Opus 4.7 I1"].notna().sum(),
    df_results["Claude Opus 4.7 I2"].notna().sum(),
    df_results["Claude Opus 4.7 I3"].notna().sum(),
    max(
        df_results["Claude Opus 4.7 I1"].notna().sum(),
        df_results["Claude Opus 4.7 I2"].notna().sum(),
        df_results["Claude Opus 4.7 I3"].notna().sum(),
    ),    
    df_results["DeepSeek V4 Pro I2"].notna().sum(),
    df_results["DeepSeek V4 Pro I3"].notna().sum(),
    df_results["DeepSeek V4 Pro I1"].notna().sum(),
    max(
        df_results["DeepSeek V4 Pro I2"].notna().sum(),
        df_results["DeepSeek V4 Pro I3"].notna().sum(),
        df_results["DeepSeek V4 Pro I1"].notna().sum(),
    )
    df_results["Grok 4.6 I1"].notna().sum(),
    df_results["Grok 4.6 I2"].notna().sum(),
    df_results["Grok 4.6 I3"].notna().sum(),
    max(
        df_results["Grok 4.6 I1"].notna().sum(),
        df_results["Grok 4.6 I2"].notna().sum(),
        df_results["Grok 4.6 I3"].notna().sum(),
    )
]