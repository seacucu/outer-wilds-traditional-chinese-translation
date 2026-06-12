using OWML.ModHelper;
using UnityEngine;

namespace OWCHT
{
    public class OWCHT : ModBehaviour
    {
        // 透過 xen.LocalizationUtility（Interplanetary Polyglot）註冊「正體中文」為新語言，
        // 不再自行 Harmony patch TextTranslation、也不再佔用簡體中文的語言槽。
        private const string LanguageName = "正體中文";

        private void Start()
        {
            var api = ModHelper.Interaction.TryGetModApi<ILocalizationAPI>("xen.LocalizationUtility");
            if (api == null)
            {
                ModHelper.Console.WriteLine("找不到 xen.LocalizationUtility，請確認前置 mod 已安裝並啟用。", OWML.Common.MessageType.Error);
                return;
            }

            DumpEnglishTranslation();   // 暫時：dump 遊戲當前版本的英文文本，比對用，完成後移除

            api.RegisterLanguage(this, LanguageName, "Translation.xml");
            api.AddLanguageFont(this, LanguageName, "Assets/owcht", "Assets/fonts/notosanstc-bold-dyn.otf", out Font font);

            if (font == null)
            {
                ModHelper.Console.WriteLine("字型載入失敗：Assets/owcht 內找不到 notosanstc-bold-dyn.otf。", OWML.Common.MessageType.Error);
            }
            else
            {
                ModHelper.Console.WriteLine($"已註冊語言「{LanguageName}」並載入字型 {font.name}。");
            }
        }

        // 暫時：把遊戲內建的英文 Translation 資產原樣寫出，供與 Translation_TC.xml 比對
        private void DumpEnglishTranslation()
        {
            // 與遊戲 TextTranslation.SetLanguage 相同的組路徑方式：Translation\<語言代碼>\Translation
            var sep = System.IO.Path.DirectorySeparatorChar;
            var assetPath = "Translation" + sep + TextTranslation.s_langFolder[(int)TextTranslation.Language.ENGLISH] + sep + "Translation";
            var asset = Resources.Load<TextAsset>(assetPath);
            if (asset == null)
            {
                ModHelper.Console.WriteLine($"Dump 失敗：找不到資產 {assetPath}。", OWML.Common.MessageType.Error);
                return;
            }
            var dumpPath = System.IO.Path.Combine(ModHelper.Manifest.ModFolderPath, "Translation_EN_dump.xml");
            System.IO.File.WriteAllText(dumpPath, asset.text, System.Text.Encoding.UTF8);
            ModHelper.Console.WriteLine($"已 dump 英文文本到 {dumpPath}");
        }
    }
}
