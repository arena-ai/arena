import React, { useEffect, useRef, useState } from 'react'
import { useTheme } from '@chakra-ui/react'
import * as d3 from 'd3'


const StackChart: React.FC<{ data: { model: string; hour: string; value: number }[] }> = ({ data }) => {
    const [width, setWidth] = useState(window.innerWidth);
    const svgRef = useRef<SVGSVGElement | null>(null)
    const theme = useTheme()
    const colors = new Map([
        ["gpt-4o", theme.colors.teal[200]],
        ["gpt-4-turbo", theme.colors.teal[300]],
        ["gpt-4", theme.colors.teal[400]],
        ["gpt-3.5-turbo", theme.colors.teal[500]],
        ["gpt-3.5-turbo-16k", theme.colors.teal[600]],
        ["mistral-large-latest", theme.colors.green[100]],
        ["mistral-medium", theme.colors.green[200]],
        ["mistral-medium-latest", theme.colors.green[300]],
        ["mistral-small", theme.colors.green[400]],
        ["mistral-small-latest", theme.colors.green[500]],
        ["mistral-tiny", theme.colors.green[600]],
        ["open-mistral-7b", theme.colors.gray[200]],
        ["open-mixtral-8x7b", theme.colors.gray[300]],
        ["claude-3-opus-20240229", theme.colors.cyan[200]],
        ["claude-3-sonnet-20240229", theme.colors.cyan[300]],
        ["claude-3-haiku-20240307", theme.colors.cyan[400]],
        ["claude-2.1", theme.colors.cyan[500]],
        ["claude-2.0", theme.colors.cyan[600]],
        ["claude-instant-1.2", theme.colors.cyan[700]],
    ])

    // Track window resize
    useEffect(() => {
        const handleResize = () => {
        setWidth(window.innerWidth);
        };

        window.addEventListener('resize', handleResize);

        // Cleanup the event listener on component unmount
        return () => {
        window.removeEventListener('resize', handleResize);
        };
    }, []);

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
            // @ts-expect-error: @types/d3 is not complete
            .value(([, group], key) => group.get(key) || 0)
            // @ts-expect-error: @types/d3 is not complete
            (reducedData);

        // Get the SVG container
        const svg = d3.select(svgRef.current)
        svg.selectAll("*").remove()

        // Set dimensions and margins
        const margin = { top: 20, right: 30, bottom: 30, left: 40 };
        const width = svg!.node()!.getBoundingClientRect().width - margin.left - margin.right;
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

        // svg.attr('width', width + margin.left + margin.right)
        svg.attr('height', height + margin.top + margin.bottom)
            .append('g')
            .attr('transform', `translate(${margin.left},${margin.top})`);
        
        // Create a tooltip div
        const tooltip = d3.select("body").append("div")
            .attr("class", "tooltip")
            .style("position", "absolute")
            .style("visibility", "hidden")
            .style("background", "#fff")
            .style("border", "1px solid #ccc")
            .style("padding", "5px")
            .style("border-radius", "3px")
            .style("box-shadow", "0 0 5px rgba(0,0,0,0.1)");

        // Add the stacked bars
        svg.selectAll('g.model')
            .data(stackedData)
            .enter().append('g')
            .attr("fill", d => colors.get(d.key))
            .on("mouseover", function (_, d) {
                tooltip.style("visibility", "visible")
                    .html(`<b>model</b>: ${d.key}`);
            })
            .on("mousemove", function (event) {
                tooltip.style("top", (event.pageY - 10) + "px")
                    .style("left", (event.pageX + 10) + "px");
            })
            .on("mouseout", function () {
                tooltip.style("visibility", "hidden");
            })
            .selectAll('rect')
            .data(d => d)
            .enter().append('rect')
            // @ts-expect-error: @types/d3 is not complete
            .attr('x', d => xScale(d.data[0]))
            .attr('y', d => yScale(d[1]))
            .attr('height', d => yScale(d[0]) - yScale(d[1]))
            .attr('width', xScale.bandwidth())

        // Add the X Axis
        svg.append('g')
            .attr('transform', `translate(0,${height})`)
            .call(d3.axisBottom(xScale));

        // Add the Y Axis
        svg.append('g')
            .call(d3.axisLeft(yScale));

    }, [data, width]);

    return <svg width="100%" ref={svgRef}></svg>;
};

export default StackChart;