# Fixed Mambo narration and publication rights

Read this reference before installing, enabling, recording, or publishing speech narration.

## Voice identification

- Fixed target voice: `曼波`. Do not make it configurable and do not substitute a similar voice.
- Reference: `https://www.bilibili.com/video/BV18RApeLEqw`, checked on 2026-07-24.
- At about 40 seconds, the tutorial's text-to-speech picker visibly selects the first cartoon-avatar voice labeled `曼波`; the video subtitle says `选择曼波音效`.
- Kokoro `zm_yunxi` (`sid=50`) is a different voice. The former mapping was incorrect and has been removed.
- The reference page states `未经作者授权，禁止转载`. Do not download, bundle, excerpt, replay, or clone its audio for narration without authorization. Temporary frame inspection for identification is not a bundled skill asset.

## Scope-specific licensing gate

No checked source currently establishes all rights needed for automated, potentially monetized video narration. Public, streamed, redistributed, or monetized narration remains fail-closed until one source supplies a written record covering:

1. the fixed Mambo voice or model and its provenance;
2. automated or API synthesis, rather than only interactive use in an editor;
3. publication in videos that may earn platform revenue;
4. redistribution terms if any runtime, weights, reference audio, or notices will be bundled;
5. a stable source URL, version, license text, and checksum for downloaded artifacts.

The local community runtime may be used only when the user explicitly states that the use is entirely personal, noncommercial, and non-public. The controller records that statement in `.runtime/personal-use.json`, reports `usage_scope: personal_noncommercial` and `publication_allowed: false`, binds both services to localhost, and fails closed when the marker or pinned runtime is absent. This narrow mode does not authorize recording for later publication, streaming, sharing generated audio, or redistributing the model/runtime.

Treat publication rights for the output and use rights for the synthesis service/model as separate questions. A personal-use statement does not resolve either question for public use.

Do not infer that a provider lacks rights merely because the voice is synthetic, and do not infer that a third party may copy the voice/model because the provider may hold only a service license. Widespread use, the absence of a visible copyright notice, and a provider's failure to prove ownership are not affirmative commercial licenses.

## Checked sources and limits

### Bcut/必剪

- Official agreement: `https://www.bilibili.com/blackboard/bcut/activity-fwyT3DYfq4.html`, version updated 2022-11-10 and effective 2022-11-17, checked on 2026-07-24.
- Section 1.3 grants a personal, revocable, non-transferable, non-exclusive, non-commercial right to use the product/service and reserves ungranted rights.
- Section 4.6.3 prohibits obtaining platform services, content, or data through robots, crawlers, automated programs, scripts, or software without prior express written permission.
- The general agreement does not expressly clear this voice for automated real-time synthesis or revenue-earning video publication. Do not reverse engineer or automate the editor service.

### MiloraAPI

- Documentation: `https://api.milorapart.top/docs/45/mbAIsc`, checked on 2026-07-24.
- The endpoint advertises a free Mambo trial with a 50-call daily IP limit and accepts narration text over the network.
- The public documentation examined does not state the voice/model provenance or grant commercial-publication rights. An MIT license on a client that calls this API covers the client code, not the hosted voice, model, or generated-audio rights.
- Do not send gameplay commentary to this provider or record its output until those terms are documented and accepted.

### Community local models

- `Tsukimisaka/MamboTTS` had no repository license when checked on 2026-07-24. Its README limits the software to personal learning, technical research, and academic exchange. This is the basis for the explicitly acknowledged local personal-use mode only; it is not publication clearance.
- Installed client/model release: `MamboTTS v1.1.0`, GitHub asset `MamboTTS-v1.1.0-full.zip`, 268,798,368 bytes, SHA-256 `e284c7bcc8b0429b5329f518f32f5d0ad04d87f7f8a2e2afd607286c3d27570e`.
- Installed engine: ModelScope `FlowerCry/gpt-sovits-7z-pacakges`, generic `GPT-SoVITS-v2pro-20250604.7z`, 8,185,086,602 bytes, SHA-256 `bd60d0796553ff05d8568136e199c13e0dc22ebe2ed24273134e34ed6f215cd6`. The generic package is used for the local RTX 4060; do not replace it with the NVIDIA 50-series package.
- Installed voice artifacts: `mambo-e15.ckpt` SHA-256 `f4ed8b5a04a64e952314ce90e542d1f3f546920475512e40a18804f03c1e395a`; `mambo_e8_s352.pth` SHA-256 `3cd36a876d5bd6b37158e4cf881cb6fa5d774c21bedb4c45c728d72481f7f41c`; `refer.wav` SHA-256 `6031533a08a3c1fc9daef66620db5c287cd48c6c3b44b3912922db1f644715da`.
- The upstream README's roughly 3.8 GB engine estimate is stale for the pinned package. The compressed engine is about 8.19 GB and extracts to about 14.13 GB, excluding the archive and client/model asset.
- Other MIT-licensed Mambo clients found during review call MiloraAPI. Their MIT licenses do not license the remote model or voice.

## Publication requirements after clearance

Once a qualified source is recorded and the controller is deliberately re-enabled, retain the fixed Mambo voice, the provider/model license record, and the platform's AI-generated-content declaration. A suitable plain-language disclosure is:

`本视频含AI生成的游戏解说文本及合成语音。`

The Measures for Labeling Artificial Intelligence-Generated Synthetic Content took effect on September 1, 2025. Article 10 requires users publishing generated synthetic content through network information services to declare it proactively and use the service provider's labeling feature. Do not remove or conceal a platform or generator label.

No additional public-video content safety mode is part of this skill. The existing Tower-P narration contract remains unchanged; only the fixed-voice licensing gate applies.
