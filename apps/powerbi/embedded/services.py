from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import requests
from django.conf import settings

from apps.core.security.services import log_security_event
from apps.powerbi.embedded.models import PowerBIReport


class PowerBIServiceError(Exception):
    pass


@dataclass
class EmbedConfig:
    type: str
    token_type: str
    access_token: str
    embed_url: str
    report_id: str
    expires_at: str | None = None


class PowerBIEmbedService:
    token_endpoint_template = '{authority}/{tenant_id}/oauth2/v2.0/token'

    @classmethod
    def is_configured(cls) -> bool:
        return all([
            settings.POWERBI_TENANT_ID,
            settings.POWERBI_CLIENT_ID,
            settings.POWERBI_CLIENT_SECRET,
        ])

    @classmethod
    def acquire_aad_token(cls) -> str:
        if not cls.is_configured():
            raise PowerBIServiceError('Power BI environment variables are not configured.')
        token_endpoint = cls.token_endpoint_template.format(
            authority=settings.POWERBI_AUTHORITY_URL.rstrip('/'),
            tenant_id=settings.POWERBI_TENANT_ID,
        )
        response = requests.post(
            token_endpoint,
            data={
                'grant_type': 'client_credentials',
                'client_id': settings.POWERBI_CLIENT_ID,
                'client_secret': settings.POWERBI_CLIENT_SECRET,
                'scope': settings.POWERBI_SCOPE,
            },
            timeout=20,
        )
        response.raise_for_status()
        payload = response.json()
        return payload['access_token']

    @classmethod
    def generate_embed_token(cls, report: PowerBIReport, aad_token: str) -> dict:
        url = f"{settings.POWERBI_API_BASE_URL}/groups/{report.workspace_id}/reports/{report.powerbi_report_id}/GenerateToken"
        response = requests.post(
            url,
            headers={
                'Authorization': f'Bearer {aad_token}',
                'Content-Type': 'application/json',
            },
            json={'accessLevel': 'View'},
            timeout=20,
        )
        response.raise_for_status()
        return response.json()

    @classmethod
    def build_embed_config(cls, report: PowerBIReport, *, user=None, property_obj=None) -> EmbedConfig:
        try:
            aad_token = cls.acquire_aad_token()
            token_payload = cls.generate_embed_token(report, aad_token)
            return EmbedConfig(
                type='report',
                token_type='Embed',
                access_token=token_payload['token'],
                embed_url=report.embed_url,
                report_id=report.powerbi_report_id,
                expires_at=token_payload.get('expiration'),
            )
        except requests.RequestException as exc:
            log_security_event(
                category='powerbi',
                event_type='embed_token_generation_failed',
                severity='error',
                user=user,
                property_obj=property_obj,
                object_repr=report.name,
                details={'error': str(exc)},
            )
            raise PowerBIServiceError(str(exc)) from exc
