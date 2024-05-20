import React, { useEffect, useRef } from 'react'
import * as d3 from 'd3'

const StackChart: React.FC<{ data: { model: string; hour: string; value: number }[] }> = ({ data }) => {
    const svgRef = useRef<SVGSVGElement | null>(null)

    useEffect(() => {
        if (!data) return

        // Group data
        const reducedData = d3.rollup(data, D => d3.sum(D, d => d.value), d => d.hour, d => d.model)

        // Flatten the data and extract unique models and hours
        const models = d3.sort(d3.union(data.map(d => d.model)))
        const hours = d3.sort(d3.union(data.map(d => d.hour)))

        // Prepare the data for stacking
        const stackedData = d3.stack()
            .keys(models)
            .value(([, group], key) => group.get(key))
            (reducedData);

        console.log(stackedData)

        // Set dimensions and margins
        const margin = { top: 20, right: 30, bottom: 30, left: 40 };
        const width = 1024 - margin.left - margin.right;
        const height = 600 - margin.top - margin.bottom;

        // Create scales
        const xScale = d3.scaleBand()
            .domain(hours)
            .range([0, width])
            .padding(0.1);

        const yScale = d3.scaleLinear()
            .domain([0, d3.max(stackedData, d => d3.max(d, d => d[1]))!])
            .nice()
            .range([height, 0]);

        const colorScale = d3.scaleOrdinal(d3.schemeCategory10)
            .domain(models);

        // Create the SVG container
        const svg = d3.select(svgRef.current)
        svg.selectAll("*").remove()
        svg.attr('width', width + margin.left + margin.right)
            .attr('height', height + margin.top + margin.bottom)
            .append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);

        // Add the stacked bars
        svg.selectAll('g')
            .data(stackedData)
            .enter().append('g')
            .attr('fill', d => colorScale(d.key)!)
            .selectAll('rect')
            .data(d => d)
            .enter().append('rect')
            .attr('x', d => xScale(d.data[0]))
            .attr('y', d => yScale(d[1]))
            .attr('height', d => yScale(d[0]) - yScale(d[1]))
            .attr('width', xScale.bandwidth());

        // Add the X Axis
        svg.append('g')
            .attr('transform', `translate(0,${height})`)
            .call(d3.axisBottom(xScale));

        // Add the Y Axis
        svg.append('g')
            .call(d3.axisLeft(yScale));

    }, [data]);

    return <svg width="100%" ref={svgRef}></svg>;
};

export default StackChart;