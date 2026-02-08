/**
 * RecurringConfig Component - Configure recurrence patterns for tasks.
 * 
 * Phase V Features:
 * - Preset recurrence patterns (daily, weekly, monthly, etc.)
 * - Custom RRule builder
 * - Visual preview of schedule
 */

import { useState, useEffect } from "react";
import { RECURRENCE_PRESETS } from "../types/task";

interface RecurringConfigProps {
    value: string | null | undefined;
    onChange: (rrule: string | null) => void;
    disabled?: boolean;
}

type RecurrencePreset = keyof typeof RECURRENCE_PRESETS | "custom" | "none";

const WEEKDAYS = [
    { short: "MO", label: "Mon" },
    { short: "TU", label: "Tue" },
    { short: "WE", label: "Wed" },
    { short: "TH", label: "Thu" },
    { short: "FR", label: "Fri" },
    { short: "SA", label: "Sat" },
    { short: "SU", label: "Sun" },
];

export default function RecurringConfig({
    value,
    onChange,
    disabled = false,
}: RecurringConfigProps) {
    const [isExpanded, setIsExpanded] = useState(false);
    const [selectedPreset, setSelectedPreset] = useState<RecurrencePreset>("none");
    const [customConfig, setCustomConfig] = useState({
        frequency: "WEEKLY",
        interval: 1,
        weekdays: ["MO"] as string[],
        monthDay: 1,
    });

    // Determine preset from value
    useEffect(() => {
        if (!value) {
            setSelectedPreset("none");
            return;
        }

        // Check if it matches a preset
        const matchedPreset = Object.entries(RECURRENCE_PRESETS).find(
            ([_, preset]) => preset.rrule === value
        );

        if (matchedPreset) {
            setSelectedPreset(matchedPreset[0] as RecurrencePreset);
        } else {
            setSelectedPreset("custom");
            // Parse the custom rule
            parseRRule(value);
        }
    }, [value]);

    const parseRRule = (rrule: string) => {
        try {
            const parts = rrule.split(";");
            const config = { ...customConfig };

            parts.forEach((part) => {
                const [key, val] = part.split("=");
                if (key === "FREQ") {
                    config.frequency = val;
                } else if (key === "INTERVAL") {
                    config.interval = parseInt(val, 10);
                } else if (key === "BYDAY") {
                    config.weekdays = val.split(",");
                } else if (key === "BYMONTHDAY") {
                    config.monthDay = parseInt(val, 10);
                }
            });

            setCustomConfig(config);
        } catch (e) {
            console.error("Failed to parse RRule:", e);
        }
    };

    const buildCustomRRule = () => {
        let rrule = `FREQ=${customConfig.frequency}`;

        if (customConfig.interval > 1) {
            rrule += `;INTERVAL=${customConfig.interval}`;
        }

        if (customConfig.frequency === "WEEKLY" && customConfig.weekdays.length > 0) {
            rrule += `;BYDAY=${customConfig.weekdays.join(",")}`;
        }

        if (customConfig.frequency === "MONTHLY") {
            rrule += `;BYMONTHDAY=${customConfig.monthDay}`;
        }

        return rrule;
    };

    const handlePresetChange = (preset: RecurrencePreset) => {
        setSelectedPreset(preset);

        if (preset === "none") {
            onChange(null);
        } else if (preset === "custom") {
            onChange(buildCustomRRule());
        } else {
            onChange(RECURRENCE_PRESETS[preset].rrule);
        }
    };

    const handleCustomConfigChange = (updates: Partial<typeof customConfig>) => {
        const newConfig = { ...customConfig, ...updates };
        setCustomConfig(newConfig);

        // Rebuild the rule
        let rrule = `FREQ=${newConfig.frequency}`;
        if (newConfig.interval > 1) {
            rrule += `;INTERVAL=${newConfig.interval}`;
        }
        if (newConfig.frequency === "WEEKLY" && newConfig.weekdays.length > 0) {
            rrule += `;BYDAY=${newConfig.weekdays.join(",")}`;
        }
        if (newConfig.frequency === "MONTHLY") {
            rrule += `;BYMONTHDAY=${newConfig.monthDay}`;
        }

        onChange(rrule);
    };

    const toggleWeekday = (day: string) => {
        const newWeekdays = customConfig.weekdays.includes(day)
            ? customConfig.weekdays.filter((d) => d !== day)
            : [...customConfig.weekdays, day];

        // Ensure at least one day is selected
        if (newWeekdays.length === 0) return;

        handleCustomConfigChange({ weekdays: newWeekdays });
    };

    const getRecurrenceDescription = () => {
        if (!value) return "Does not repeat";
        if (selectedPreset !== "custom" && selectedPreset !== "none") {
            return RECURRENCE_PRESETS[selectedPreset].label;
        }
        return describeCustomRule();
    };

    const describeCustomRule = () => {
        const { frequency, interval, weekdays, monthDay } = customConfig;
        let desc = interval > 1 ? `Every ${interval} ` : "Every ";

        switch (frequency) {
            case "DAILY":
                desc += interval > 1 ? "days" : "day";
                break;
            case "WEEKLY":
                desc += interval > 1 ? "weeks" : "week";
                if (weekdays.length > 0 && weekdays.length < 7) {
                    desc += ` on ${weekdays.join(", ")}`;
                }
                break;
            case "MONTHLY":
                desc += interval > 1 ? "months" : "month";
                desc += ` on day ${monthDay}`;
                break;
            case "YEARLY":
                desc += interval > 1 ? "years" : "year";
                break;
        }

        return desc;
    };

    return (
        <div className="space-y-3">
            {/* Collapsed View */}
            <button
                type="button"
                onClick={() => setIsExpanded(!isExpanded)}
                disabled={disabled}
                className={`w-full flex items-center justify-between px-4 py-3 rounded-xl transition-all ${disabled
                        ? "bg-white/5 text-gray-600 cursor-not-allowed"
                        : "bg-white/5 hover:bg-white/10 text-gray-300 hover:text-white"
                    }`}
            >
                <div className="flex items-center gap-3">
                    <svg
                        className={`w-5 h-5 ${value ? "text-blue-400" : "text-gray-500"}`}
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                        />
                    </svg>
                    <span className="text-sm">{getRecurrenceDescription()}</span>
                </div>
                <svg
                    className={`w-4 h-4 transition-transform ${isExpanded ? "rotate-180" : ""}`}
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
            </button>

            {/* Expanded Configuration */}
            {isExpanded && !disabled && (
                <div className="p-4 bg-white/5 rounded-xl space-y-4 animate-fade-in">
                    {/* Preset Options */}
                    <div className="space-y-2">
                        <label className="text-xs text-gray-500 uppercase tracking-wider">Quick options:</label>
                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                            <button
                                type="button"
                                onClick={() => handlePresetChange("none")}
                                className={`px-3 py-2 rounded-lg text-xs font-medium transition-all ${selectedPreset === "none"
                                        ? "bg-white/15 text-white ring-1 ring-white/30"
                                        : "bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white"
                                    }`}
                            >
                                No repeat
                            </button>
                            {Object.entries(RECURRENCE_PRESETS).slice(0, 5).map(([key, { label }]) => (
                                <button
                                    key={key}
                                    type="button"
                                    onClick={() => handlePresetChange(key as RecurrencePreset)}
                                    className={`px-3 py-2 rounded-lg text-xs font-medium transition-all ${selectedPreset === key
                                            ? "bg-blue-500/20 text-blue-400 ring-1 ring-blue-500/50"
                                            : "bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white"
                                        }`}
                                >
                                    {label}
                                </button>
                            ))}
                            <button
                                type="button"
                                onClick={() => handlePresetChange("custom")}
                                className={`px-3 py-2 rounded-lg text-xs font-medium transition-all ${selectedPreset === "custom"
                                        ? "bg-purple-500/20 text-purple-400 ring-1 ring-purple-500/50"
                                        : "bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white"
                                    }`}
                            >
                                Custom...
                            </button>
                        </div>
                    </div>

                    {/* Custom Configuration */}
                    {selectedPreset === "custom" && (
                        <div className="space-y-4 pt-4 border-t border-white/10">
                            {/* Frequency */}
                            <div className="space-y-2">
                                <label className="text-xs text-gray-500 uppercase tracking-wider">Repeat:</label>
                                <div className="flex gap-2">
                                    <span className="text-sm text-gray-400 self-center">Every</span>
                                    <input
                                        type="number"
                                        min="1"
                                        max="99"
                                        value={customConfig.interval}
                                        onChange={(e) =>
                                            handleCustomConfigChange({ interval: Math.max(1, parseInt(e.target.value) || 1) })
                                        }
                                        className="w-16 bg-white/10 border border-white/20 rounded-lg px-2 py-1.5 text-white text-sm text-center focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                                    />
                                    <select
                                        value={customConfig.frequency}
                                        onChange={(e) => handleCustomConfigChange({ frequency: e.target.value })}
                                        className="bg-white/10 border border-white/20 rounded-lg px-3 py-1.5 text-white text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                                    >
                                        <option value="DAILY">Day(s)</option>
                                        <option value="WEEKLY">Week(s)</option>
                                        <option value="MONTHLY">Month(s)</option>
                                        <option value="YEARLY">Year(s)</option>
                                    </select>
                                </div>
                            </div>

                            {/* Weekday Selector (for weekly) */}
                            {customConfig.frequency === "WEEKLY" && (
                                <div className="space-y-2">
                                    <label className="text-xs text-gray-500 uppercase tracking-wider">On days:</label>
                                    <div className="flex gap-1">
                                        {WEEKDAYS.map(({ short, label }) => (
                                            <button
                                                key={short}
                                                type="button"
                                                onClick={() => toggleWeekday(short)}
                                                className={`w-10 h-10 rounded-lg text-xs font-medium transition-all ${customConfig.weekdays.includes(short)
                                                        ? "bg-blue-500/30 text-blue-400 ring-1 ring-blue-500/50"
                                                        : "bg-white/5 text-gray-500 hover:bg-white/10 hover:text-white"
                                                    }`}
                                            >
                                                {label}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Month Day Selector (for monthly) */}
                            {customConfig.frequency === "MONTHLY" && (
                                <div className="space-y-2">
                                    <label className="text-xs text-gray-500 uppercase tracking-wider">On day:</label>
                                    <input
                                        type="number"
                                        min="1"
                                        max="31"
                                        value={customConfig.monthDay}
                                        onChange={(e) =>
                                            handleCustomConfigChange({
                                                monthDay: Math.min(31, Math.max(1, parseInt(e.target.value) || 1)),
                                            })
                                        }
                                        className="w-20 bg-white/10 border border-white/20 rounded-lg px-3 py-1.5 text-white text-sm text-center focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                                    />
                                </div>
                            )}

                            {/* Preview */}
                            <div className="pt-3 border-t border-white/10">
                                <p className="text-sm text-gray-400">
                                    <span className="text-gray-500">Preview:</span> {describeCustomRule()}
                                </p>
                                <p className="text-xs text-gray-600 mt-1 font-mono">{value}</p>
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
