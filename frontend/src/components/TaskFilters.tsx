/**
 * TaskFilters Component - Search, filter, and sort controls for tasks.
 * 
 * Phase V Features:
 * - Keyword search
 * - Priority filter
 * - Tags filter
 * - Due date range
 * - Sort options
 */

import { useState, useEffect, useCallback } from "react";
import {
    TaskFilters as TaskFiltersType,
    Priority,
    SortField,
    SortOrder,
    PRIORITY_LABELS,
    PRIORITY_COLORS,
    TAG_PRESETS,
} from "../types/task";

interface TaskFiltersProps {
    filters: TaskFiltersType;
    onFilterChange: (filters: TaskFiltersType) => void;
    availableTags?: string[];
}

export default function TaskFilters({
    filters,
    onFilterChange,
    availableTags = TAG_PRESETS,
}: TaskFiltersProps) {
    const [isExpanded, setIsExpanded] = useState(false);
    const [localKeyword, setLocalKeyword] = useState(filters.keyword || "");

    // Debounce keyword search
    useEffect(() => {
        const timer = setTimeout(() => {
            const currentKeyword = filters.keyword || "";
            const newKeyword = localKeyword || "";
            if (newKeyword !== currentKeyword) {
                onFilterChange({ ...filters, keyword: localKeyword || undefined });
            }
        }, 300);
        return () => clearTimeout(timer);
    }, [localKeyword, filters, onFilterChange]);

    const handlePriorityChange = (priority: Priority | null) => {
        onFilterChange({ ...filters, priority });
    };

    const handleTagToggle = (tag: string) => {
        const currentTags = filters.tags || [];
        const newTags = currentTags.includes(tag)
            ? currentTags.filter((t) => t !== tag)
            : [...currentTags, tag];
        onFilterChange({ ...filters, tags: newTags.length > 0 ? newTags : undefined });
    };

    const handleSortChange = (sort_by: SortField) => {
        const newOrder = filters.sort_by === sort_by && filters.sort_order === "asc" ? "desc" : "asc";
        onFilterChange({ ...filters, sort_by, sort_order: newOrder });
    };

    const handleDateChange = (field: "due_date_from" | "due_date_to", value: string) => {
        onFilterChange({ ...filters, [field]: value || undefined });
    };

    const clearAllFilters = () => {
        setLocalKeyword("");
        onFilterChange({
            status: "all",
            priority: null,
            tags: undefined,
            keyword: undefined,
            due_date_from: undefined,
            due_date_to: undefined,
            sort_by: "created_at",
            sort_order: "desc",
        });
    };

    const hasActiveFilters =
        filters.priority ||
        (filters.tags && filters.tags.length > 0) ||
        filters.keyword ||
        filters.due_date_from ||
        filters.due_date_to;

    return (
        <div className="glass-card rounded-2xl p-6 space-y-4">
            {/* Search Bar */}
            <div className="relative">
                <input
                    type="text"
                    value={localKeyword}
                    onChange={(e) => setLocalKeyword(e.target.value)}
                    placeholder="Search tasks..."
                    className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 pl-11 text-white placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all"
                />
                <svg
                    className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                >
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                    />
                </svg>
                {localKeyword && (
                    <button
                        onClick={() => setLocalKeyword("")}
                        className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white transition-colors"
                    >
                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                )}
            </div>

            {/* Quick Filters Row */}
            <div className="flex items-center gap-3 flex-wrap">
                {/* Priority Pills */}
                <div className="flex items-center gap-2">
                    <span className="text-xs text-gray-500 uppercase tracking-wider">Priority:</span>
                    {(["HIGH", "MEDIUM", "LOW"] as Priority[]).map((priority) => (
                        <button
                            key={priority}
                            onClick={() => handlePriorityChange(filters.priority === priority ? null : priority)}
                            className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all ${filters.priority === priority
                                ? "bg-white/20 text-white ring-2"
                                : "bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white"
                                }`}
                            style={{
                                borderColor: filters.priority === priority ? PRIORITY_COLORS[priority] : undefined,
                                ringColor: filters.priority === priority ? PRIORITY_COLORS[priority] : undefined,
                            }}
                        >
                            <span
                                className="inline-block w-2 h-2 rounded-full mr-1.5"
                                style={{ backgroundColor: PRIORITY_COLORS[priority] }}
                            />
                            {PRIORITY_LABELS[priority]}
                        </button>
                    ))}
                </div>

                {/* Toggle Advanced Filters */}
                <button
                    onClick={() => setIsExpanded(!isExpanded)}
                    className="ml-auto flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white text-xs transition-all"
                >
                    <svg
                        className={`w-4 h-4 transition-transform ${isExpanded ? "rotate-180" : ""}`}
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                    >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                    {isExpanded ? "Less filters" : "More filters"}
                </button>

                {/* Clear Filters */}
                {hasActiveFilters && (
                    <button
                        onClick={clearAllFilters}
                        className="px-3 py-1.5 rounded-lg bg-red-500/10 text-red-400 hover:bg-red-500/20 text-xs transition-all"
                    >
                        Clear all
                    </button>
                )}
            </div>

            {/* Expanded Filters */}
            {isExpanded && (
                <div className="pt-4 border-t border-white/10 space-y-4 animate-fade-in">
                    {/* Tags */}
                    <div className="space-y-2">
                        <span className="text-xs text-gray-500 uppercase tracking-wider">Tags:</span>
                        <div className="flex flex-wrap gap-2">
                            {availableTags.map((tag) => (
                                <button
                                    key={tag}
                                    onClick={() => handleTagToggle(tag)}
                                    className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all ${filters.tags?.includes(tag)
                                        ? "bg-blue-500/20 text-blue-400 ring-1 ring-blue-500/50"
                                        : "bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white"
                                        }`}
                                >
                                    #{tag}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Due Date Range */}
                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <label className="text-xs text-gray-500 uppercase tracking-wider">Due from:</label>
                            <input
                                type="date"
                                value={filters.due_date_from || ""}
                                onChange={(e) => handleDateChange("due_date_from", e.target.value)}
                                className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="text-xs text-gray-500 uppercase tracking-wider">Due to:</label>
                            <input
                                type="date"
                                value={filters.due_date_to || ""}
                                onChange={(e) => handleDateChange("due_date_to", e.target.value)}
                                className="w-full bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                            />
                        </div>
                    </div>

                    {/* Sort Options */}
                    <div className="space-y-2">
                        <span className="text-xs text-gray-500 uppercase tracking-wider">Sort by:</span>
                        <div className="flex flex-wrap gap-2">
                            {([
                                { field: "created_at", label: "Created" },
                                { field: "due_date", label: "Due Date" },
                                { field: "priority", label: "Priority" },
                                { field: "title", label: "Title" },
                            ] as { field: SortField; label: string }[]).map(({ field, label }) => (
                                <button
                                    key={field}
                                    onClick={() => handleSortChange(field)}
                                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${filters.sort_by === field
                                        ? "bg-white/15 text-white"
                                        : "bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white"
                                        }`}
                                >
                                    {label}
                                    {filters.sort_by === field && (
                                        <svg
                                            className={`w-3.5 h-3.5 transition-transform ${filters.sort_order === "desc" ? "rotate-180" : ""
                                                }`}
                                            fill="none"
                                            viewBox="0 0 24 24"
                                            stroke="currentColor"
                                        >
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                                        </svg>
                                    )}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
