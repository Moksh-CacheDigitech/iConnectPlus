"use client";

import { useEffect, type RefObject } from "react";

function isScrollableY(el: HTMLElement): boolean {
  const { overflowY } = getComputedStyle(el);
  if (overflowY !== "auto" && overflowY !== "scroll" && overflowY !== "overlay") {
    return false;
  }
  return el.scrollHeight > el.clientHeight + 1;
}

function isHorizontalOnlyScrollport(el: HTMLElement): boolean {
  const { overflowX, overflowY } = getComputedStyle(el);
  const xScrollable =
    (overflowX === "auto" || overflowX === "scroll") &&
    el.scrollWidth > el.clientWidth + 1;
  // overflow-x:auto forces overflow-y to compute to auto even with no vertical overflow,
  // which makes Chromium treat the node as a scrollport and eat vertical wheel.
  const forcedYPort =
    (overflowX === "auto" || overflowX === "scroll") &&
    (overflowY === "auto" || overflowY === "scroll" || overflowY === "overlay") &&
    !isScrollableY(el);
  return xScrollable || forcedYPort;
}

/**
 * When the cursor is over a horizontal table wrapper (`overflow-x: auto`), browsers
 * often trap vertical wheel/trackpad gestures. Forward those deltas to the page main
 * scroller so the workspace stays scrollable.
 */
export function useMainScrollChain(mainRef: RefObject<HTMLElement | null>) {
  useEffect(() => {
    const main = mainRef.current;
    if (!main) return;

    const onWheel = (event: WheelEvent) => {
      if (event.ctrlKey || event.defaultPrevented) return;
      if (event.deltaY === 0) return;
      if (Math.abs(event.deltaY) < Math.abs(event.deltaX)) return;

      let node: HTMLElement | null =
        event.target instanceof Element ? (event.target as HTMLElement) : null;
      let hitHorizontalOnly = false;

      while (node && node !== main) {
        if (isScrollableY(node)) {
          const atTop = node.scrollTop <= 0 && event.deltaY < 0;
          const atBottom =
            node.scrollTop + node.clientHeight >= node.scrollHeight - 1 &&
            event.deltaY > 0;
          if (!atTop && !atBottom) return;
          break;
        }
        if (isHorizontalOnlyScrollport(node)) {
          hitHorizontalOnly = true;
        }
        node = node.parentElement;
      }

      if (!hitHorizontalOnly) return;

      const max = main.scrollHeight - main.clientHeight;
      if (max <= 1) return;

      const next = Math.min(max, Math.max(0, main.scrollTop + event.deltaY));
      if (next === main.scrollTop) return;

      main.scrollTop = next;
      event.preventDefault();
    };

    main.addEventListener("wheel", onWheel, { passive: false, capture: true });
    return () => main.removeEventListener("wheel", onWheel, { capture: true });
  }, [mainRef]);
}
