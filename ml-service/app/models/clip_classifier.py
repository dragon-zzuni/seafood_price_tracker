"""
OpenAI CLIP 기반 품목 분류 모듈
"""
from __future__ import annotations

from typing import List, Sequence, Optional

import logging

import numpy as np
import torch
from PIL import Image
import open_clip

from .base import ClassificationModel, ClassificationResult

logger = logging.getLogger(__name__)


class CLIPClassifier(ClassificationModel):
    """
    OpenAI CLIP 모델을 사용한 수산물 품목 분류기
    Detection 단계에서 잘라낸 바운딩 박스를 입력 받아
    각 품목에 대한 유사도 점수를 계산한다.
    """

    DEFAULT_MODEL_NAME = "ViT-B-32"
    DEFAULT_PRETRAINED = "openai"
    DEFAULT_PROMPT_TEMPLATE = "a photo of {}"
    DEFAULT_LABELS: Sequence[str] = (
        "광어",
        "우럭",
        "참돔",
        "연어",
        "돌돔",
        "감성돔",
        "방어",
        "민어",
        "농어",
        "고등어",
        "대게",
        "킹크랩",
        "코끼리조개",
        "왕우럭조개",
        "전복",
        "멍게",
        "해삼",
        "개불",
        "낙지",
        "참소라",
        "새우",
        "갑오징어",
    )

    def __init__(
        self,
        model_name: Optional[str] = None,
        pretrained: Optional[str] = None,
        device: Optional[str] = None,
        class_labels: Optional[Sequence[str]] = None,
        prompt_template: Optional[str] = None,
        auto_load: bool = True,
    ) -> None:
        self.model_name = model_name or self.DEFAULT_MODEL_NAME
        self.pretrained = pretrained or self.DEFAULT_PRETRAINED
        resolved_device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.device = torch.device(resolved_device)
        self.class_labels = tuple(class_labels) if class_labels else self.DEFAULT_LABELS
        self.prompt_template = prompt_template or self.DEFAULT_PROMPT_TEMPLATE

        self.model = None
        self.preprocess = None
        self.tokenizer = None
        self.text_features = None

        if auto_load:
            self.load_model()

    def load_model(self, model_path: str | None = None) -> None:
        """
        CLIP 모델 로딩

        Args:
            model_path: "MODEL::PRETRAINED" 형태로 전달할 수 있는 커스텀 식별자
                        (미지정 시 기본값 사용)
        """
        model_name, pretrained = self._resolve_identifier(model_path)
        logger.info(
            "CLIP Classification 모델 로딩 시작: model=%s, pretrained=%s, device=%s",
            model_name,
            pretrained,
            self.device,
        )

        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            model_name=model_name,
            pretrained=pretrained,
            device=self.device,
        )
        self.tokenizer = open_clip.get_tokenizer(model_name)
        self.model_name = model_name
        self.pretrained = pretrained

        self._build_text_features()

        logger.info("CLIP Classification 모델 로딩 완료")

    def classify(self, image: np.ndarray) -> List[ClassificationResult]:
        if self.model is None or self.preprocess is None or self.text_features is None:
            raise RuntimeError("CLIP 모델이 초기화되지 않았습니다. load_model()을 먼저 호출하세요.")

        if image.size == 0:
            logger.warning("입력 이미지가 비어 있습니다.")
            return []

        pil_image = Image.fromarray(image.astype(np.uint8))
        image_tensor = self.preprocess(pil_image).unsqueeze(0).to(self.device)

        with torch.no_grad():
            image_features = self.model.encode_image(image_tensor)
            image_features /= image_features.norm(dim=-1, keepdim=True)

            logits = (
                self.model.logit_scale.exp() * image_features @ self.text_features.T
            ).squeeze(0)
            probabilities = logits.softmax(dim=-1).cpu().numpy()

        results: List[ClassificationResult] = []
        for idx, (label, confidence) in enumerate(zip(self.class_labels, probabilities)):
            results.append(
                ClassificationResult(
                    item_id=idx,
                    item_name=label,
                    confidence=float(confidence),
                )
            )

        results.sort(key=lambda r: r.confidence, reverse=True)
        return results

    # ------------------------------------------------------------------ #
    # 내부 유틸리티
    # ------------------------------------------------------------------ #
    def _resolve_identifier(self, identifier: str | None) -> tuple[str, str]:
        """
        "MODEL::PRETRAINED" 형식 또는 단일 모델명을 파싱한다.
        """
        if identifier:
            if "::" in identifier:
                model_name, pretrained = identifier.split("::", 1)
                return model_name.strip(), pretrained.strip()
            return identifier.strip(), self.pretrained
        return self.model_name, self.pretrained

    def _build_text_features(self) -> None:
        prompts = [self.prompt_template.format(label) for label in self.class_labels]

        with torch.no_grad():
            tokenized = self.tokenizer(prompts).to(self.device)
            text_features = self.model.encode_text(tokenized)
            text_features /= text_features.norm(dim=-1, keepdim=True)

        self.text_features = text_features
        logger.info("CLIP 텍스트 임베딩 %d개 생성 완료", len(prompts))
