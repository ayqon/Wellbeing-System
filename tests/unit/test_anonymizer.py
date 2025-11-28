import pytest
from src.utils.privacy import Anonymizer

def test_anonymizer_initialization():
    anonymizer = Anonymizer()
    assert hasattr(anonymizer, '_salt')

def test_mask_identity_returns_string():
    anonymizer = Anonymizer()
    user_id = "user123"
    masked = anonymizer.mask_identity(user_id)
    assert isinstance(masked, str)
    assert masked != user_id

def test_mask_identity_consistency():
    anonymizer = Anonymizer()
    user_id = "user123"
    masked1 = anonymizer.mask_identity(user_id)
    masked2 = anonymizer.mask_identity(user_id)
    assert masked1 == masked2

def test_mask_identity_uniqueness():
    anonymizer = Anonymizer()
    user_id1 = "user123"
    user_id2 = "user456"
    masked1 = anonymizer.mask_identity(user_id1)
    masked2 = anonymizer.mask_identity(user_id2)
    assert masked1 != masked2
