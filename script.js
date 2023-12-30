const minAngle = -150;
const maxAngle = 150;
const range = maxAngle - minAngle;
let currentValue = 50; // Initial value (between 0 and 100)

const svg = d3.select("#gauge")
    .attr("width", 300)
    .attr("height", 300);

const gauge = svg.append("g")
    .attr("transform", "translate(150, 150)");

const backgroundArc = d3.arc()
    .innerRadius(80)
    .outerRadius(100)
    .startAngle(deg2rad(minAngle))
    .endAngle(deg2rad(maxAngle));

gauge.append("path")
    .attr("class", "background")
    .attr("d", backgroundArc);

const valueArc = d3.arc()
    .innerRadius(80)
    .outerRadius(100);

const valuePath = gauge.append("path")
    .datum({ endAngle: deg2rad(minAngle) })
    .attr("class", "value")
    .attr("d", valueArc);

const knob = d3.select("#knob");

// Attach knob drag behavior
knob.call(d3.drag()
    .on("start", dragstarted)
    .on("drag", dragged)
    .on("end", dragended));

updateGauge(currentValue);

function deg2rad(deg) {
    return (deg - 90) * Math.PI / 180;
}

function arcTween(d) {
    const interpolate = d3.interpolate(d.endAngle, d.endAngle);
    return function (t) {
        d.endAngle = interpolate(t);
        return valueArc(d);
    };
}

function dragstarted(event) {
    d3.select(this).raise().classed("active", true);
}

function dragged(event) {
    const x = event.x - 150;
    const y = event.y - 150;
    const angle = Math.atan2(y, x) * 180 / Math.PI;
    if (angle >= minAngle && angle <= maxAngle) {
        currentValue = ((angle - minAngle) / range) * 100;
        updateGauge(currentValue);
    }
}

function dragended(event) {
    d3.select(this).classed("active", false);
}

function updateGauge(value) {
    knob.style("transform", `rotate(${minAngle + (range * value / 100)}deg)`);
    valuePath.transition()
        .duration(1000)
        .attrTween("d", arcTween);
}
