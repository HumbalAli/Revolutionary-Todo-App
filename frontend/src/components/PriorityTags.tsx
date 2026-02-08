/**
 * PriorityTags Component - Priority selector and tag input for tasks.
 * 
 * Phase V Features:
 * - Visual priority selection (HIGH/MEDIUM/LOW)
 * - Tag input with autocomplete
 * - Preset tag suggestions
 */

import { useState, useRef, useEffect } from "react";
import {
    Priority,
    PRIORITY_LABELS,
    PRIORITY_COLORS,
    TAG_PRESETS,
} from "../types/task";

interface PriorityTagsProps {
    priority: Priority | null | undefined;
    tags: string[];
    onPriorityChange: (priority: Priority | null) => void;
    onTagsChange: (tags: string[]) => void;
    disabled?: boolean;
    availableTags?: string[];
}

export default function PriorityTags({
    priority,
    tags,
    onPriorityChange,
    onTagsChange,
    disabled = false,
    availableTags = TAG_PRESETS,
}: PriorityTagsProps) {
    const [tagInput, setTagInput] = useState("");
    const [showSuggestions, setShowSuggestions] = useState(false);
    const inputRef = useRef<HTMLInputElement>(null);
    const suggestionsRef = useRef<HTMLDivElement>(null);

    // Close suggestions on outside click
    useEffect(() => {
        const handleClickOutside = (e: MouseEvent) => {
            if (
                suggestionsRef.current &&
                !suggestionsRef.current.contains(e.target as Node) &&
                inputRef.current &&
                !inputRef.current.contains(e.target as Node)
            ) {
                setShowSuggestions(false);
            }
        };

        document.addEventListener("mousedown", handleClickOutside);
        return () => document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    const handleAddTag = (tag: string) => {
        const normalizedTag = tag.trim().toLowerCase().replace(/[^a-z0-9-_]/g, "");
        if (normalizedTag && !tags.includes(normalizedTag)) {
            onTagsChange([...tags, normalizedTag]);
        }
        setTagInput("");
        setShowSuggestions(false);
        inputRef.current?.focus();
    };

    const handleRemoveTag = (tagToRemove: string) => {
        onTagsChange(tags.filter((t) => t !== tagToRemove));
    };

    const handleInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === "Enter" || e.key === ",") {
            e.preventDefault();
            if (tagInput.trim()) {
                handleAddTag(tagInput);
            }
        } else if (e.key === "Backspace" && !tagInput && tags.length > 0) {
            // Remove last tag when backspace on empty input
            handleRemoveTag(tags[tags.length - 1]);
        } else if (e.key === "Escape") {
            setShowSuggestions(false);
        }
    };

    const filteredSuggestions = availableTags.filter(
        (tag) =>
            tag.toLowerCase().includes(tagInput.toLowerCase()) &&
            !tags.includes(tag)
    );

    return (
        <div className="space-y-4">
            {/* Priority Selector */}
            <div className="space-y-2">
                <label className="text-xs text-gray-500 uppercase tracking-wider flex items-center gap-2">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9"
                        />
                    </svg>
                    Priority
                </label>
                <div className="flex gap-2">
                    {(["HIGH", "MEDIUM", "LOW"] as Priority[]).map((p) => (
                        <button
                            key={p}
                            type="button"
                            onClick={() => onPriorityChange(priority === p ? null : p)}
                            disabled={disabled}
                            className={`flex-1 relative px-4 py-2.5 rounded-xl text-sm font-medium transition-all overflow-hidden group ${disabled ? "opacity-50 cursor-not-allowed" : ""
                                } ${priority === p
                                    ? "text-white ring-2"
                                    : "bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white"
                                }`}
                            style={{
                                backgroundColor: priority === p ? `${PRIORITY_COLORS[p]}20` : undefined,
                                ringColor: priority === p ? PRIORITY_COLORS[p] : undefined,
                            }}
                        >
                            {/* Background gradient on hover */}
                            <div
                                className="absolute inset-0 opacity-0 group-hover:opacity-10 transition-opacity"
                                style={{
                                    background: `linear-gradient(135deg, ${PRIORITY_COLORS[p]} 0%, transparent 100%)`,
                                }}
                            />

                            {/* Priority indicator dot */}
                            <span className="relative flex items-center justify-center gap-2">
                                <span
                                    className={`w-2.5 h-2.5 rounded-full transition-all ${priority === p ? "scale-100" : "scale-75 opacity-50"
                                        }`}
                                    style={{ backgroundColor: PRIORITY_COLORS[p] }}
                                />
                                {PRIORITY_LABELS[p]}
                            </span>

                            {/* Selected checkmark */}
                            {priority === p && (
                                <span className="absolute right-2 top-1/2 -translate-y-1/2">
                                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                        <path
                                            fillRule="evenodd"
                                            d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                                            clipRule="evenodd"
                                        />
                                    </svg>
                                </span>
                            )}
                        </button>
                    ))}
                </div>
            </div>

            {/* Tags Input */}
            <div className="space-y-2">
                <label className="text-xs text-gray-500 uppercase tracking-wider flex items-center gap-2">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"
                        />
                    </svg>
                    Tags
                </label>

                <div className="relative">
                    {/* Tags Container */}
                    <div
                        className={`flex flex-wrap gap-2 p-3 bg-white/5 rounded-xl border border-white/10 min-h-[52px] transition-all ${disabled ? "opacity-50" : "focus-within:ring-2 focus-within:ring-blue-500/50"
                            }`}
                    >
                        {/* Existing Tags */}
                        {tags.map((tag) => (
                            <span
                                key={tag}
                                className="inline-flex items-center gap-1 px-2.5 py-1 bg-blue-500/20 text-blue-400 rounded-lg text-sm animate-scale-in"
                            >
                                #{tag}
                                {!disabled && (
                                    <button
                                        type="button"
                                        onClick={() => handleRemoveTag(tag)}
                                        className="ml-0.5 hover:text-white transition-colors"
                                    >
                                        <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path
                                                strokeLinecap="round"
                                                strokeLinejoin="round"
                                                strokeWidth={2}
                                                d="M6 18L18 6M6 6l12 12"
                                            />
                                        </svg>
                                    </button>
                                )}
                            </span>
                        ))}

                        {/* Tag Input */}
                        {!disabled && (
                            <input
                                ref={inputRef}
                                type="text"
                                value={tagInput}
                                onChange={(e) => {
                                    setTagInput(e.target.value);
                                    setShowSuggestions(true);
                                }}
                                onFocus={() => setShowSuggestions(true)}
                                onKeyDown={handleInputKeyDown}
                                placeholder={tags.length === 0 ? "Add tags..." : ""}
                                className="flex-1 min-w-[100px] bg-transparent border-none outline-none text-white text-sm placeholder:text-gray-600"
                            />
                        )}
                    </div>

                    {/* Tag Suggestions Dropdown */}
                    {showSuggestions && filteredSuggestions.length > 0 && !disabled && (
                        <div
                            ref={suggestionsRef}
                            className="absolute z-10 top-full left-0 right-0 mt-1 py-2 bg-gray-900/95 backdrop-blur-lg border border-white/10 rounded-xl shadow-xl max-h-48 overflow-y-auto animate-fade-in"
                        >
                            {filteredSuggestions.map((suggestion) => (
                                <button
                                    key={suggestion}
                                    type="button"
                                    onClick={() => handleAddTag(suggestion)}
                                    className="w-full px-4 py-2 text-left text-sm text-gray-300 hover:bg-white/10 hover:text-white transition-colors"
                                >
                                    <span className="text-gray-500">#</span>
                                    {suggestion}
                                </button>
                            ))}
                        </div>
                    )}
                </div>

                {/* Quick Tag Suggestions */}
                {!disabled && tags.length < 5 && (
                    <div className="flex flex-wrap gap-1.5 mt-2">
                        {availableTags
                            .filter((tag) => !tags.includes(tag))
                            .slice(0, 6)
                            .map((tag) => (
                                <button
                                    key={tag}
                                    type="button"
                                    onClick={() => handleAddTag(tag)}
                                    className="px-2 py-0.5 text-xs text-gray-500 hover:text-blue-400 hover:bg-blue-500/10 rounded transition-all"
                                >
                                    +{tag}
                                </button>
                            ))}
                    </div>
                )}
            </div>
        </div>
    );
}
