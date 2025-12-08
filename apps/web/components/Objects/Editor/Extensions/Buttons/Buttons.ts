import { ReactNodeViewRenderer } from "@tiptap/react";
import { mergeAttributes, Node } from "@tiptap/core";
import ButtonsExtension from "./ButtonsExtension";

export default Node.create({
  name: "button",
  group: "block",
  draggable: true,
  content: "text*",

  addAttributes() {
    return {
      emoji: {
        default: '🔗',
      },
      label: {
        default: 'Change button text',
      },
      link: {
        default: '',
      },
      color: {
        default: 'greeen',
      },
      alignment: {
        default: 'center',
      },
    };
  },

  parseHTML() {
    return [
      {
        tag: "button-block",
      },
    ];
  },

  renderHTML({ HTMLAttributes }) {
    return ["button-block", mergeAttributes(HTMLAttributes), 0];
  },

  addNodeView() {
    return ReactNodeViewRenderer(ButtonsExtension);
  },
});