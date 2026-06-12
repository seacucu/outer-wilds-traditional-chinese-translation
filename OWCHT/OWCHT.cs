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
    }
}
