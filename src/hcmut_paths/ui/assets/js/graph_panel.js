(function(window, document) {
    function collapsePanel() {
        document.getElementById("graph-content").style.display = "none";
        document.getElementById("graph-panel").style.width = "250px";
        document.getElementById("graph-panel").style.height = "60px";
    }

    function expandPanel() {
        document.getElementById("graph-content").style.display = "block";
        document.getElementById("graph-panel").style.width = "430px";
        document.getElementById("graph-panel").style.height = "700px";
    }

    function bindGraphPanel() {
        const panel = document.getElementById("graph-panel");

        if (!panel || panel.dataset.bound === "true") {
            return;
        }

        panel.dataset.bound = "true";

        document.getElementById("graph-panel-expand").addEventListener(
            "click",
            expandPanel
        );
        document.getElementById("graph-panel-collapse").addEventListener(
            "click",
            collapsePanel
        );

        panel.querySelectorAll("[data-vertex-id]").forEach(function(element) {
            element.addEventListener("click", function() {
                window.HcmutMapInteractions.focusVertex(
                    element.dataset.vertexId
                );
            });
        });

        panel.querySelectorAll("[data-edge-id]").forEach(function(element) {
            element.addEventListener("click", function() {
                window.HcmutMapInteractions.focusEdgeById(
                    element.dataset.edgeId
                );
            });
        });
    }

    window.collapsePanel = collapsePanel;
    window.expandPanel = expandPanel;

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", bindGraphPanel);
    } else {
        bindGraphPanel();
    }
})(window, document);
