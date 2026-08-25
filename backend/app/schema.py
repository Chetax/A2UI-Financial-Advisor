"""
A2UI schema — the contract between the LLM and the renderer.
"""
from __future__ import annotations

from typing import Annotated, List, Literal, Optional, Union

from pydantic import BaseModel, Field


# --------------------------------------------------------------------------- #
# Shared building blocks
# --------------------------------------------------------------------------- #
class Action(BaseModel):
    """An interaction the frontend sends back to the agent when triggered."""
    id: str = Field(..., description="Stable identifier the agent uses to route the interaction")
    payload: Optional[dict] = Field(default=None, description="Optional static data attached to the action")



class TextProps(BaseModel):
    content: str
    variant: Literal["heading", "subheading", "body", "caption", "metric", "label"] = "body"


class TextComponent(BaseModel):
    type: Literal["text"]
    props: TextProps


class ButtonProps(BaseModel):
    label: str
    action: Action
    variant: Literal["primary", "secondary", "ghost"] = "primary"


class ButtonComponent(BaseModel):
    type: Literal["button"]
    props: ButtonProps


class TextFieldProps(BaseModel):
    name: str = Field(..., description="Key this field contributes to the form submit payload")
    label: str
    placeholder: Optional[str] = ""
    value: Optional[str] = ""
    inputType: Literal["text", "number", "email"] = "text"


class TextFieldComponent(BaseModel):
    type: Literal["text-field"]
    props: TextFieldProps


# --------------------------------------------------------------------------- #
# Branch components (recursive children)
# --------------------------------------------------------------------------- #
class ContainerProps(BaseModel):
    direction: Literal["row", "column"] = "column"
    gap: int = 12
    align: Optional[Literal["start", "center", "end", "stretch"]] = None


class ContainerComponent(BaseModel):
    type: Literal["container"]
    props: ContainerProps = ContainerProps()
    children: List["Component"] = Field(default_factory=list)


class CardProps(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None


class CardComponent(BaseModel):
    type: Literal["card"]
    props: CardProps = CardProps()
    children: List["Component"] = Field(default_factory=list)


class FormProps(BaseModel):
    submitLabel: str = "Submit"
    action: Action


class FormComponent(BaseModel):
    type: Literal["form"]
    props: FormProps
    children: List["Component"] = Field(default_factory=list)


# --------------------------------------------------------------------------- #
# The discriminated union — this is what makes validation strict + recursive
# --------------------------------------------------------------------------- #
Component = Annotated[
    Union[
        ContainerComponent,
        CardComponent,
        TextComponent,
        ButtonComponent,
        TextFieldComponent,
        FormComponent,
    ],
    Field(discriminator="type"),
]


class A2UIResponse(BaseModel):
    """Top-level envelope the agent returns for every turn."""
    message: Optional[str] = Field(
        default=None,
        description="Short conversational lead-in shown above the rendered component",
    )
    component: Component


# Recursive models need an explicit rebuild once `Component` is defined.
for _model in (ContainerComponent, CardComponent, FormComponent, A2UIResponse):
    _model.model_rebuild()